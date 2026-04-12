"""Normalize security dependency updates across project manifests.

This script keeps the repository's dependency manifests aligned after
`pip-audit --fix` rewrites vulnerable requirement specifiers to exact pins.
It converts direct `==` pins into lower-bound `>=` constraints and syncs
matching dependency entries from the requirements files into `pyproject.toml`.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from packaging.requirements import InvalidRequirement, Requirement
from packaging.utils import canonicalize_name

DEFAULT_PYPROJECT_PATH = Path("pyproject.toml")
DEFAULT_REQUIREMENT_PATHS = (
    Path("requirements.txt"),
    Path("requirements-dev.txt"),
    Path("docs/requirements.txt"),
)
QUOTED_STRING_PATTERN = re.compile(r'"([^"\n]+)"')


@dataclass(frozen=True)
class SyncResult:
    """Describe whether a manifest file changed.

    Attributes:
        path: The manifest path that was processed.
        changed: Whether the manifest contents were updated.
    """

    path: Path
    changed: bool


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        The parsed command line namespace.
    """

    parser = argparse.ArgumentParser(
        description=(
            "Normalize pip-audit fixes and sync shared dependency specifiers "
            "across requirements files and pyproject.toml."
        )
    )
    parser.add_argument(
        "--pyproject",
        type=Path,
        default=DEFAULT_PYPROJECT_PATH,
        help="Path to the pyproject.toml file to sync.",
    )
    parser.add_argument(
        "--requirements",
        type=Path,
        nargs="*",
        default=list(DEFAULT_REQUIREMENT_PATHS),
        help="Requirements files to normalize before syncing pyproject.toml.",
    )
    return parser.parse_args()


def _build_minimum_requirement_string(
    requirement: Requirement,
    minimum_version: str,
) -> str:
    """Build a lower-bound requirement string.

    Args:
        requirement: The parsed requirement to rebuild.
        minimum_version: The minimum safe version.

    Returns:
        A requirement string using a `>=` lower bound.
    """

    extras = f"[{','.join(sorted(requirement.extras))}]" if requirement.extras else ""
    marker = f"; {requirement.marker}" if requirement.marker else ""
    return f"{requirement.name}{extras}>={minimum_version}{marker}"


def normalize_requirement_string(requirement_string: str) -> str:
    """Convert an exact pin into a lower-bound dependency constraint.

    Args:
        requirement_string: A dependency requirement string.

    Returns:
        The normalized requirement string. Non-requirement strings and
        non-exact specifiers are returned unchanged.
    """

    try:
        requirement = Requirement(requirement_string)
    except InvalidRequirement:
        return requirement_string

    specifiers = list(requirement.specifier)
    exact_specifiers = [
        specifier
        for specifier in specifiers
        if specifier.operator == "==" and "*" not in specifier.version
    ]
    if len(specifiers) != 1 or len(exact_specifiers) != 1:
        return requirement_string

    return _build_minimum_requirement_string(requirement, exact_specifiers[0].version)


def _split_requirement_comment(line: str) -> tuple[str, str]:
    """Split an inline requirements comment from a dependency line.

    Args:
        line: A single requirements file line without a trailing newline.

    Returns:
        A tuple of `(requirement_portion, comment_portion)`.
    """

    if " #" not in line or line.lstrip().startswith("#"):
        return line, ""
    requirement_part, _, comment = line.partition(" #")
    return requirement_part, f" #{comment}"


def normalize_requirements_file(path: Path) -> tuple[SyncResult, dict[str, str]]:
    """Normalize exact pins inside a requirements file.

    Args:
        path: The requirements file path to update.

    Returns:
        A tuple containing the file update result and a mapping of canonical
        package name to normalized requirement string for successfully parsed
        dependencies in the file.
    """

    original_text = path.read_text(encoding="utf-8")
    dependency_map: dict[str, str] = {}
    normalized_lines: list[str] = []

    for line in original_text.splitlines(keepends=True):
        stripped_line = line.strip()
        if (
            not stripped_line
            or stripped_line.startswith("#")
            or stripped_line.startswith("-")
        ):
            normalized_lines.append(line)
            continue

        newline = "\n" if line.endswith("\n") else ""
        line_without_newline = line[:-1] if newline else line
        requirement_part, comment_part = _split_requirement_comment(
            line_without_newline
        )
        leading_whitespace = requirement_part[
            : len(requirement_part) - len(requirement_part.lstrip())
        ]
        trailing_whitespace = requirement_part[len(requirement_part.rstrip()) :]
        requirement_string = requirement_part.strip()
        normalized_requirement = normalize_requirement_string(requirement_string)
        normalized_line = (
            f"{leading_whitespace}{normalized_requirement}"
            f"{trailing_whitespace}{comment_part}{newline}"
        )
        normalized_lines.append(normalized_line)

        try:
            parsed_requirement = Requirement(normalized_requirement)
        except InvalidRequirement:
            continue

        dependency_map[canonicalize_name(parsed_requirement.name)] = (
            normalized_requirement
        )

    normalized_text = "".join(normalized_lines)
    if normalized_text != original_text:
        path.write_text(normalized_text, encoding="utf-8")

    return (
        SyncResult(path=path, changed=normalized_text != original_text),
        dependency_map,
    )


def sync_pyproject_file(path: Path, dependency_map: dict[str, str]) -> SyncResult:
    """Sync dependency specifiers inside `pyproject.toml`.

    Args:
        path: The `pyproject.toml` path to update.
        dependency_map: Normalized dependency strings keyed by canonical name.

    Returns:
        The file update result.
    """

    original_text = path.read_text(encoding="utf-8")
    changed = False

    def replace_requirement(match: re.Match[str]) -> str:
        """Rewrite dependency-like strings inside the TOML file.

        Args:
            match: A regex match for a quoted TOML string.

        Returns:
            The updated quoted string.
        """

        nonlocal changed

        raw_value = match.group(1)
        normalized_value = normalize_requirement_string(raw_value)

        try:
            parsed_requirement = Requirement(normalized_value)
        except InvalidRequirement:
            return match.group(0)

        replacement = dependency_map.get(
            canonicalize_name(parsed_requirement.name),
            normalized_value,
        )
        if replacement != raw_value:
            changed = True
        return f'"{replacement}"'

    synchronized_text = QUOTED_STRING_PATTERN.sub(replace_requirement, original_text)
    if synchronized_text != original_text:
        path.write_text(synchronized_text, encoding="utf-8")

    return SyncResult(path=path, changed=synchronized_text != original_text or changed)


def sync_manifests(
    pyproject_path: Path,
    requirement_paths: Sequence[Path],
) -> list[SyncResult]:
    """Normalize and synchronize all configured manifests.

    Args:
        pyproject_path: The `pyproject.toml` file to update.
        requirement_paths: Requirements files that drive dependency versions.

    Returns:
        The ordered sync results for each processed manifest.
    """

    dependency_map: dict[str, str] = {}
    results: list[SyncResult] = []

    for requirement_path in requirement_paths:
        requirement_result, file_dependency_map = normalize_requirements_file(
            requirement_path
        )
        dependency_map.update(file_dependency_map)
        results.append(requirement_result)

    results.append(sync_pyproject_file(pyproject_path, dependency_map))
    return results


def _format_changed_paths(results: Iterable[SyncResult]) -> list[str]:
    """Collect changed file paths for user-facing output.

    Args:
        results: The manifest sync results.

    Returns:
        Relative path strings for files that changed.
    """

    return [str(result.path) for result in results if result.changed]


def main() -> int:
    """Run the manifest normalization workflow.

    Returns:
        A process exit code.
    """

    args = parse_args()
    results = sync_manifests(args.pyproject, args.requirements)
    changed_paths = _format_changed_paths(results)
    if changed_paths:
        print("Updated manifests:")
        for changed_path in changed_paths:
            print(f"- {changed_path}")
    else:
        print("No manifest changes were needed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
