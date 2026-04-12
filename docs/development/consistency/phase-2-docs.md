# Phase 2: Docs

Set the shell variables from `index.md` first. Run every command from the
repository root.

## Objective

Make the published docs truthful, navigable, and consistent with the code and
workflows.

## 1. Audit The Docs Surface

```bash
rg --files docs
rg '^nav:' -A 200 mkdocs.yml
rg 'pre-commit|make |Python 3\.[0-9]|pytest|mypy|black|isort|flake8' README.md docs
```

Use the output to find stale version claims, missing pages, and commands that
no longer match the repo.

## 2. Normalize The Docs Structure

- Keep `docs/index.md`, `getting-started/`, `api/`, `reference/`, and
  `development/` aligned with the other libraries.
- Add this `docs/development/consistency/` runbook set to the nav so it is a
  first-class docs surface instead of an orphaned directory.
- Keep examples and changelog pages current enough that release notes, docs,
  and README do not contradict each other.
- If the repo has both a root `STYLE_GUIDE.md` and a docs copy, define which
  one owns content and cross-link the other.

## 3. Normalize Contributor Guidance

- Ensure contributor docs use the real repo URL, the real Python version
  floor, and the real install and test commands.
- Remove references to `pre-commit`, `make`, helper scripts, or docs pages
  that do not exist, or add the missing files as part of the same pass.
- Make release docs match the actual workflow behavior and publish mechanism.

## 4. Validate Docs Locally

```bash
python -m pip install --upgrade pip
python -m pip install -e .
python -m pip install -r docs/requirements.txt
mkdocs build --strict
```

## Done When

- Every nav item resolves.
- README, docs, and contributing guidance say the same thing.
- Docs build locally without ignored breakage.
- The consistency runbooks are linked from `mkdocs.yml`.
