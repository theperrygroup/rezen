# ReZEN Docs Build Fix

## Problem Summary

`mkdocs build --strict` is currently failing from the repository root.

The first confirmed failure is a strict MkDocs warning:

- `docs/STYLE_GUIDE.md` exists in the documentation tree but is not included in `mkdocs.yml` navigation.

This is also part of a larger documentation drift issue where contributor-facing docs do not fully match the repository's actual workflow, supported Python versions, and release/deployment setup.

## Reproduction Steps

Run these commands from the repository root:

```bash
python -m pip install -e .
python -m pip install -r docs/requirements.txt
mkdocs build --strict
```

Observed failure:

- MkDocs warns that `STYLE_GUIDE.md` exists under `docs/` but is not included in `nav`.
- Under `--strict`, warnings fail the build.

## Fix Steps

1. Decide and document the canonical style-guide ownership between:
   - `STYLE_GUIDE.md`
   - `docs/STYLE_GUIDE.md`
2. Update `mkdocs.yml` so all intended docs pages remain correctly linked in navigation.
3. Clean up contributor-facing docs to match the current repository reality:
   - supported Python versions from `pyproject.toml`
   - install commands actually supported by the repo
   - CI quality checks from `.github/workflows/ci.yml`
   - deployment/release flow from `.github/workflows/unified-deployment.yml`
4. Remove or correct stale instructions such as:
   - outdated clone path/repo naming
   - stale upstream remote guidance
   - `pre-commit` setup instructions when no `.pre-commit-config.yaml` exists
   - references to nonexistent `docs.yml` or `release.yml` workflows
5. Rebuild docs strictly and verify no new warnings are introduced.

## Verification Steps

Run from the repository root:

```bash
python -m pip install -e .
python -m pip install -r docs/requirements.txt
mkdocs build --strict
```

Optional follow-up checks after doc edits:

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

## Rollback / Mitigation

- If the docs build must be unblocked immediately, temporarily restore navigation coverage for any edited doc pages in `mkdocs.yml`.
- Revert only the documentation/config truthfulness changes related to the failure if a later edit introduces new MkDocs warnings.
- Do not revert unrelated runtime or API files.
