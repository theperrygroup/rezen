# Consistency Runbooks

Use this directory to align `rezen` with the shared Perry Group Python client
standard used across `vestaboard`, `rezen`, `flex_mls`, and `wfrmls`. Run
every command from the repository root.

## Local Variables

```bash
export PACKAGE_TARGET="rezen"
export CI_WORKFLOW=".github/workflows/ci.yml"
export RELEASE_WORKFLOW=".github/workflows/unified-deployment.yml"
export DOCS_WORKFLOW=".github/workflows/unified-deployment.yml"
export DEPENDENCY_AUTOMATION_FILE=".github/dependabot.yml"
```

## Runbooks

- [`shared-standard.md`](shared-standard.md)
- [`phase-1-foundation.md`](phase-1-foundation.md)
- [`phase-2-docs.md`](phase-2-docs.md)
- [`phase-3-github-actions.md`](phase-3-github-actions.md)
- [`repo-gap-map.md`](repo-gap-map.md)

## Working Rules

- Read `shared-standard.md` before changing files.
- Finish the phases in order so metadata and docs stop drifting before
  workflows are updated.
- Treat missing files or missing workflow steps as gaps to close, not as
  reasons to skip a phase.
- Record intentional exceptions in `repo-gap-map.md` so this repo does not
  silently diverge from the other libraries.

## Definition Of Done

- `pyproject.toml`, `rezen/__init__.py`, and the release workflow all
  describe the same version story.
- Tooling advertised in docs or config is either enforced in CI or removed
  from the published standard.
- The docs nav matches real files and the consistency runbooks are first-class
  docs pages.
- CI, release, security, and dependency automation cover the same baseline
  outcomes as the other libraries even if the implementation details differ.
