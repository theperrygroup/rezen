# Rezen Gap Map

Use this file with the phase docs. The commands below assume the variables
from `index.md` are already exported.

## Snapshot

| Area | Current state |
| --- | --- |
| Package target | `rezen` |
| Python floor | `>=3.8` in `pyproject.toml` |
| Release flow | `.github/workflows/unified-deployment.yml` |
| Docs flow | Also inside `.github/workflows/unified-deployment.yml` |
| Security flow | `.github/workflows/ci.yml` and `.github/workflows/security-audit.yml` |
| Dependency automation | Dependabot via `.github/dependabot.yml` |
| Style guides | Root `STYLE_GUIDE.md` and `docs/STYLE_GUIDE.md` both exist |

## Phase 1 Priorities

- `pyproject.toml`, `.flake8`, `.github/workflows/ci.yml`, and
  `.github/workflows/unified-deployment.yml`: collapse the multiple Flake8
  sources of truth into one documented standard.
- `pyproject.toml`: `pylint` is still part of the dev toolchain even though the
  workflows do not enforce it.
- `pyproject.toml` and CI: coverage reporting exists, but the repo does not
  enforce the threshold described elsewhere in docs and style guidance.
- `pyproject.toml`: `mypy` targets Python 3.9 even though the package supports
  Python 3.8 through 3.12.
- `requirements.txt`, `requirements-dev.txt`, `docs/requirements.txt`, and
  `pyproject.toml`: document the dependency source of truth.

## Phase 1 Commands

```bash
rg 'flake8|pylint|python_version = "3.9"|coverage' pyproject.toml .flake8 .github/workflows/ci.yml .github/workflows/unified-deployment.yml
rg --files -g 'requirements*.txt' -g 'docs/requirements.txt' .
rg '^version = ' pyproject.toml
rg '^__version__ = ' rezen/__init__.py
python -m build
python -m twine check dist/*
```

## Phase 2 Priorities

- `docs/development/contributing.md`: update the Python floor, clone URLs, and
  contributor setup steps so they match the real repo.
- `docs/development/contributing.md`: remove or fulfill the `pre-commit`
  guidance, because no `.pre-commit-config.yaml` exists.
- `STYLE_GUIDE.md` and `docs/STYLE_GUIDE.md`: define which copy owns updates
  and cross-link the other.
- `docs/`: keep the newly added consistency runbooks aligned with deployment
  and contributor docs so this repo does not create a second docs drift path.

## Phase 2 Commands

```bash
rg '3\.7|rezen-python-client|original-org|pre-commit' docs/development/contributing.md
rg '^nav:' -A 220 mkdocs.yml
python -m pip install -e .
python -m pip install -r docs/requirements.txt
mkdocs build --strict
```

## Phase 3 Priorities

- `.github/workflows/ci.yml` and `.github/workflows/unified-deployment.yml`:
  remove duplicated quality logic where possible so the two files do not drift.
- `.github/workflows/release.yml` and `.github/workflows/docs.yml`: decide
  whether the deprecated workflows should remain in-tree or be removed.
- `.github/workflows/ci.yml`: if `flake8-docstrings` and
  `flake8-import-order` stay installed, decide whether they are informational
  only or real gates.
- `.github/workflows/unified-deployment.yml`: keep the version parity checks,
  but verify that docs build, package build, and release steps all point at the
  same commands described in the docs.

## Phase 3 Commands

```bash
rg 'flake8-docstrings|flake8-import-order|mypy|pytest|mkdocs|pip-audit|bandit|twine|codecov' .github/workflows/ci.yml .github/workflows/unified-deployment.yml .github/workflows/security-audit.yml
rg --files .github | rg 'dependabot|renovate|docs|release'
black --check .
isort --check-only .
flake8 .
mypy "$PACKAGE_TARGET"
pytest --cov="$PACKAGE_TARGET"
mkdocs build --strict
python -m build
python -m twine check dist/*
```

## Recommended Order

1. Collapse config duplication and decide what the real local toolchain is.
2. Fix contributor guidance so the published docs match the repository.
3. Reduce workflow duplication between CI and unified deployment.
4. Keep deprecated workflow files only if they still add value after the
   unified path is cleaned up.
