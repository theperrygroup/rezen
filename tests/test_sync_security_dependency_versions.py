"""Tests for the security dependency sync helper."""

from __future__ import annotations

from pathlib import Path

from tools.sync_security_dependency_versions import (
    normalize_requirement_string,
    sync_manifests,
)


def test_normalize_requirement_string_converts_exact_pin_to_lower_bound() -> None:
    """Convert exact pins into lower-bound requirement specifiers."""

    normalized = normalize_requirement_string("mkdocstrings[python]==0.24.0")

    assert normalized == "mkdocstrings[python]>=0.24.0"


def test_sync_manifests_updates_requirements_and_pyproject(tmp_path: Path) -> None:
    """Synchronize normalized requirement versions into `pyproject.toml`."""

    pyproject_path = tmp_path / "pyproject.toml"
    requirements_path = tmp_path / "requirements.txt"
    requirements_dev_path = tmp_path / "requirements-dev.txt"
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    docs_requirements_path = docs_dir / "requirements.txt"

    pyproject_path.write_text(
        "[build-system]\n"
        'requires = ["setuptools==80.0.0"]\n'
        'build-backend = "setuptools.build_meta"\n'
        "\n"
        "[project]\n"
        'name = "rezen-test"\n'
        'version = "0.0.1"\n'
        "dependencies = [\n"
        '    "requests>=2.31.0",\n'
        '    "pydantic>=2.5.0",\n'
        "]\n"
        "\n"
        "[project.optional-dependencies]\n"
        "dev = [\n"
        '    "python-dotenv>=1.0.0",\n'
        "]\n",
        encoding="utf-8",
    )
    requirements_path.write_text("requests==2.32.3\npydantic>=2.5.0\n", encoding="utf-8")
    requirements_dev_path.write_text("python-dotenv==1.1.0\n", encoding="utf-8")
    docs_requirements_path.write_text(
        "# Documentation dependencies\nmkdocs==1.6.1\n",
        encoding="utf-8",
    )

    results = sync_manifests(
        pyproject_path=pyproject_path,
        requirement_paths=(
            requirements_path,
            requirements_dev_path,
            docs_requirements_path,
        ),
    )

    assert any(result.changed for result in results)
    assert requirements_path.read_text(encoding="utf-8") == (
        "requests>=2.32.3\npydantic>=2.5.0\n"
    )
    assert requirements_dev_path.read_text(encoding="utf-8") == "python-dotenv>=1.1.0\n"
    assert docs_requirements_path.read_text(encoding="utf-8") == (
        "# Documentation dependencies\nmkdocs>=1.6.1\n"
    )

    pyproject_text = pyproject_path.read_text(encoding="utf-8")
    assert '"setuptools>=80.0.0"' in pyproject_text
    assert '"requests>=2.32.3"' in pyproject_text
    assert '"python-dotenv>=1.1.0"' in pyproject_text
