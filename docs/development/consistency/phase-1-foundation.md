# Phase 1: Foundation

Set the shell variables from `index.md` first. Run every command from the
repository root.

## Objective

Make packaging, metadata, versioning, and tool configuration consistent before
touching docs nav or GitHub Actions.

## 1. Capture The Current State

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m pip install build twine
rg '^version = ' pyproject.toml
rg '^__version__ = ' "$PACKAGE_TARGET/__init__.py"
rg 'requires-python|license|authors|maintainers|Homepage|Documentation|Repository' pyproject.toml
rg --files -g 'requirements*.txt' -g 'docs/requirements.txt' .
rg '\[tool\.|black|isort|flake8|mypy|pytest|coverage|pylint|pydocstyle|bandit' pyproject.toml
```

If the manifest scan returns fewer files than you expect, record that decision
in `repo-gap-map.md` instead of silently accepting drift.

## 2. Normalize Metadata

- Add missing `license`, authors/maintainers, project URLs, and accurate
  Python classifiers.
- Make sure the published package name, import package name, and README wording
  tell the same story.
- Ensure `LICENSE` exists when `pyproject.toml` points to a license file.
- Keep version data synchronized between `pyproject.toml` and
  `$PACKAGE_TARGET/__init__.py`.

## 3. Choose The Dependency Source Of Truth

- Decide whether the repo is `pyproject.toml`-first or whether it
  intentionally keeps companion `requirements*.txt` files.
- If duplicate dependency manifests remain, document the sync rule in
  contributor docs and the gap map.
- Keep docs dependencies either in `docs/requirements.txt`, a `docs` extra, or
  a generated file, but not as unsynchronized duplicates.

## 4. Align Tool Configuration With Reality

- Every configured quality tool should have one local command and one CI step.
- If `flake8` is configured in multiple places, collapse to one authoritative
  config or document the loader or plugin that makes the second config active.
- If coverage targets are documented, the coverage threshold must be enforced,
  not just described.
- If the repo ships `py.typed`, confirm it is included in the build output.

## 5. Validate The Foundation

```bash
black --check .
isort --check-only .
flake8 .
mypy "$PACKAGE_TARGET"
python -m build
python -m twine check dist/*
```

## Done When

- Package metadata is complete and consistent.
- Versioning is explicit and release-ready.
- Dependency files have one documented source of truth.
- Tool configuration and local commands are no longer aspirational.
