# Deployment Guide

This repository currently relies on two contributor-facing GitHub Actions workflows:

- `.github/workflows/ci.yml`
- `.github/workflows/unified-deployment.yml`

Older references to separate `docs.yml` or `release.yml` workflows are no longer accurate for this repository.

## Continuous Integration

`ci.yml` runs on pushes and pull requests targeting `main` and `develop`.

It currently performs three stages:

1. **Code quality and security**
   - Uses Python 3.11
   - Installs `.[dev]` plus `bandit`, `pip-audit`, `flake8-docstrings`, and `flake8-import-order`
   - Runs Black, isort, flake8, mypy, Bandit, dependency auditing, and YAML/TOML validation
2. **Test matrix**
   - Runs `pytest` on Python 3.8, 3.9, 3.10, 3.11, and 3.12
   - Uses `REZEN_API_KEY` from repository secrets when tests need it
3. **Package build**
   - Builds the package with `python -m build`
   - Verifies artifacts with `twine check`

## Unified Deployment

`unified-deployment.yml` handles both documentation deployment and releases.

### Triggers

- Tag pushes matching `v*`
- Pushes to `main` that touch `docs/**`, `mkdocs.yml`, `rezen/**`, or the workflow file itself
- Manual `workflow_dispatch`

### Docs-Only Deployments

Docs deployment happens when:

- a qualifying change lands on `main`, or
- the workflow is run manually with `deploy_docs_only=true`

In that path the workflow:

- reruns code quality and tests
- installs docs and development dependencies
- refreshes the generated API coverage include file
- builds the MkDocs site
- deploys the site to GitHub Pages

### Release Deployments

Release deployment happens when:

- a `v*` tag is pushed, or
- the workflow is run manually with a `version` input

For manual releases, the workflow updates both `pyproject.toml` and `rezen/__init__.py`, creates the release commit and tag, and pushes them before continuing with the rest of the pipeline.

The release path then:

- reruns quality checks and tests
- builds the package
- publishes to PyPI
- builds and deploys documentation
- creates a GitHub release

## Secrets and Permissions

The workflows currently depend on these secrets or built-in tokens:

- `REZEN_API_KEY` for test jobs
- `PYPI_API_TOKEN` for PyPI publishing
- `GITHUB_TOKEN`, which GitHub Actions provides automatically

`unified-deployment.yml` also requests write access for repository contents, Pages, packages, and OIDC tokens because it tags releases, publishes packages, and deploys GitHub Pages.

## Local Verification

Before changing docs, packaging, or deployment behavior, these are the most useful local checks:

```bash
python -m pip install -e ".[dev]"
python -m pip install -r docs/requirements.txt
pytest
python -m build
mkdocs build --strict
```

If you only need to validate the docs build path from a clean repository checkout, this is the exact command sequence used in the docs cleanup task:

```bash
python -m pip install -e .
python -m pip install -r docs/requirements.txt
mkdocs build --strict
```

## What the Repository Does Not Use

- There is no standalone `.github/workflows/docs.yml`.
- There is no standalone `.github/workflows/release.yml`.
- There is no `.pre-commit-config.yaml`.

Keeping those details out of contributor docs helps the human docs stay aligned with the actual automation that exists in the repository today.
