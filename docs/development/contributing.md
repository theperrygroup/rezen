# Contributing Guide

Thank you for contributing to the ReZEN Python client. This page keeps the contributor workflow aligned with the repository's actual configuration in `pyproject.toml`, `.github/workflows/ci.yml`, and `.github/workflows/unified-deployment.yml`.

## Prerequisites

- Python 3.8 or newer. The package requires 3.8+, and CI currently tests 3.8 through 3.12.
- Git and a GitHub account.
- An optional `REZEN_API_KEY` if you need to run live/manual checks. Unit tests should not require a real API key.

## Clone the Repository

If you contribute through a fork, clone your fork and add the canonical repository as `upstream`:

```bash
git clone https://github.com/<your-username>/rezen.git
cd rezen
git remote add upstream https://github.com/theperrygroup/rezen.git
```

If you already have direct access to the main repository, clone `https://github.com/theperrygroup/rezen.git` and skip the `upstream` remote.

## Set Up a Local Environment

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m pip install -r docs/requirements.txt
```

The repository also includes `requirements-dev.txt`, but the editable extras install above is the path CI uses for development dependencies.

## Run the Same Checks CI Cares About

```bash
pytest
black --check --diff --line-length=88 .
isort --check-only --diff --profile=black --line-length=88 .
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics
mypy rezen/ --strict --ignore-missing-imports
python -m build
mkdocs build --strict
```

CI also runs Bandit, `pip-audit`, and YAML/TOML validation in addition to the commands above.

## Style-Guide Ownership

- [`STYLE_GUIDE.md`](https://github.com/theperrygroup/rezen/blob/main/STYLE_GUIDE.md) is the canonical guide for code style, typing, docstrings, and contributor-facing conventions.
- [`docs/STYLE_GUIDE.md`](../STYLE_GUIDE.md) is the companion guide for Markdown pages and MkDocs content.
- This repository does not currently include a `.pre-commit-config.yaml`, so contributor docs should point to direct commands rather than `pre-commit install`.

## Pull Requests

1. Branch from `main`.
2. Keep changes focused and update tests or docs when behavior changes.
3. Run the local checks above before opening a pull request, especially if you touched packaging, workflows, or docs.
4. Push your branch to your fork and open the pull request against `main`.

CI runs on pushes and pull requests targeting `main` and `develop`, so contributors may see the same validation jobs on both branches.

## Commit Messages

Use descriptive commit messages. Recent repository history commonly uses prefixes such as `docs:`, `fix:`, `refactor:`, and `chore:`, but the important part is that the message clearly explains the change.

## Documentation Changes

When documentation changes overlap with code behavior, update the relevant user-facing pages in the same change set. Common touch points include:

- `README.md`
- `docs/api/`
- `docs/guides/`
- `docs/reference/changelog.md`

## Release and Deployment Changes

If your change affects packaging, releases, or GitHub Pages deployment, also review the [Deployment Guide](deployment.md) before you open the pull request.
