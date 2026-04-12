# Shared Standard

Set the shell variables from `index.md` before running any command in this
document.

## What Must Match Across All Four Repositories

- One top-level package, `tests/`, `docs/`, and `examples/`.
- `pyproject.toml` as the canonical place for package metadata and tool
  configuration.
- Google-style docstrings, strong type hints, and a shipped `py.typed` marker.
- MkDocs Material plus `mkdocstrings` for docs.
- A GitHub Actions baseline that covers formatting, linting, typing, tests,
  docs, builds, release checks, and security.
- One explicit dependency automation strategy for root dependencies, docs
  dependencies, and GitHub Actions.

## Packaging And Metadata

- Keep version data in exactly two places: `pyproject.toml` and
  `$PACKAGE_TARGET/__init__.py`.
- Ensure `license`, authors/maintainers, `requires-python`, classifiers, and
  `[project.urls]` are present and accurate.
- Ship `py.typed` and verify it is included in built artifacts.
- If `requirements.txt`, `requirements-dev.txt`, or `docs/requirements.txt`
  exist, document which file is authoritative and how the others stay in sync.
- If the repo is intentionally `pyproject.toml`-only, document that choice
  instead of carrying stale duplicate manifests.

## Tooling And Local Quality Gates

- Standard baseline: Black, isort, flake8, mypy, pytest with coverage,
  `build`, and `twine`.
- Optional tools such as `pylint`, `pydocstyle`, `bandit`, `pip-audit`, or
  `pre-commit` are allowed only when the repo also documents and enforces them.
- If a tool is configured but never run locally or in CI, either add the
  enforcement step or remove the dead configuration.
- Local contributor instructions should match the exact commands that CI uses.

## Docs And Contributor Guidance

- Keep a real MkDocs nav: every nav entry should map to an existing markdown
  file.
- Keep a single source of truth for style guidance. If a second copy exists
  inside `docs/`, cross-link it and explicitly state which file owns updates.
- Ensure README, docs guides, contributing instructions, release docs, and
  changelog all agree on Python support, install commands, quality commands,
  and release flow.
- If docs recommend `pre-commit install`, `make quality`, or other helper
  commands, the supporting files must exist.

## GitHub Actions Baseline

- CI should fail on formatting, import order, lint, typing, tests, and build
  errors.
- Docs should be built with `mkdocs build --strict` before deploy.
- Releases should check tag-to-version parity before publishing.
- Security automation should cover dependency audits and static analysis on a
  schedule or in CI.
- Dependency automation should update root pip dependencies, docs dependencies,
  and GitHub Actions with one consistent tool across the repo set.

## Recommended Validation Session

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m pip install -r docs/requirements.txt
python -m pip install build twine
black --check .
isort --check-only .
flake8 .
mypy "$PACKAGE_TARGET"
pytest --cov="$PACKAGE_TARGET"
mkdocs build --strict
python -m build
python -m twine check dist/*
```

## Decision Rules For Exceptions

- Keep API-specific modules, examples, and workflow file names repo-specific.
- Keep behavior consistent even when implementation differs. A single unified
  deployment workflow is acceptable if it covers the same gates as separate
  `ci.yml`, `docs.yml`, and `release.yml` files.
- When a repo cannot match the standard yet, write the gap, the owning file,
  and the next command in `repo-gap-map.md`.
