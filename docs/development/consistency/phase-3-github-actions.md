# Phase 3: GitHub Actions

Set the shell variables from `index.md` first. Run every command from the
repository root.

## Objective

Bring CI, release, docs deploy, security, and dependency automation into the
same behavioral baseline used across the repo set.

## 1. Inventory The Workflow Surface

```bash
rg --files .github/workflows
rg 'black|isort|flake8|mypy|pytest|mkdocs|build|twine|bandit|pip-audit|safety|gh-action-pypi-publish|codecov' .github/workflows
rg --files .github | rg 'dependabot|renovate'
```

Confirm that each advertised quality gate has a workflow step and that each
workflow has a clear purpose.

## 2. Normalize CI Behavior

- CI should fail on formatting, import order, lint, typing, tests, and build
  issues.
- Prefer one source of truth for quality commands between local docs and
  workflows.
- If docs are part of the published surface, build them with
  `mkdocs build --strict` before deploy.
- If a job runs with `--exit-zero`, `continue-on-error`, or shell fallbacks
  that hide failure, document the reason or remove the bypass.

## 3. Normalize Release And Docs Deployment

- Require tag-to-version parity between `vX.Y.Z`, `pyproject.toml`, and
  `$PACKAGE_TARGET/__init__.py`.
- Build artifacts and run `python -m twine check dist/*` before publishing.
- Keep one clear story for docs deploy: dedicated workflow or a release or CI
  job, but not duplicated stale workflows.
- Prefer one publishing mechanism across the repo set. OIDC trusted publishing
  is preferred. Token publishing is acceptable only when documented.

## 4. Normalize Security And Dependency Automation

- Keep scheduled dependency audits and static analysis.
- Use one dependency automation tool across the repo set. The recommended
  default is `Dependabot`. If this repo keeps Renovate, record that as an
  intentional exception.
- Cover root pip dependencies, docs dependencies, and GitHub Actions
  dependencies.

## 5. Validate The Workflow Contract Locally

```bash
black --check .
isort --check-only .
flake8 .
mypy "$PACKAGE_TARGET"
pytest --cov="$PACKAGE_TARGET"
mkdocs build --strict
python -m build
python -m twine check dist/*
```

## Done When

- Workflow responsibilities are clear and non-overlapping.
- Quality gates in CI match the repo's documented standard.
- Release behavior is deterministic and version-checked.
- Security and dependency automation are explicit, scheduled, and consistent.
