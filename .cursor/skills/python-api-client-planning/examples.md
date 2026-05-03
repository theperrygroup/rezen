# Python API Client Planning Examples

## Example 1: Scaffold From A Docs URL

Prompt:

```text
Create a multi-phase plan and starter scaffold for a typed Python client based
on https://api.example.com/docs. Mirror the ReZEN-style baseline with docs,
tests, coverage, GitHub Actions, and repo rules.
```

Expected behavior:

- audit the docs URL first
- look for linked OpenAPI or Swagger artifacts
- create `docs/planning/<initiative-slug>/`
- create `.cursor/rules/`
- scaffold package, tests, docs, examples, and workflows
- leave endpoint implementation for later phases unless the user asks for more

## Example 2: Scaffold From Local `docs/api/`

Prompt:

```text
Use the checked-in docs under `docs/api/` and any local OpenAPI files to build
the planning tree and starter scaffold for our Python API client library.
```

Expected behavior:

- read `docs/api/index.md` first if it exists
- inventory the local API pages and schema artifacts
- record contradictions between prose docs and schema files
- create the full planning tree, rules, and starter scaffold

## Example 3: Extend An Existing Planning Tree

Prompt:

```text
Extend the existing API client planning docs with a new phase for workflow and
release automation. Keep the current planning root and update the active plan if
needed.
```

Expected behavior:

- read the existing landing README, artifact index, execution docs, and
  workflow tracker first
- extend the canonical active plan instead of spawning a competing one
- update only the rules and scaffold surfaces that the new phase actually
  changes

## Example 4: Refresh After Work Lands

Prompt:

```text
Refresh the API client planning docs after we landed the pytest suite, coverage
config, and MkDocs site. Keep the roadmap honest and sync the readiness
trackers.
```

Expected behavior:

- inspect checked-in tests, coverage config, docs, and workflows first
- update focused trackers, readiness overview, and execution ledger in that
  order
- avoid upgrading planned endpoint coverage into completed coverage without
  proof

## Example 5: Consolidate After Multiple Slices

Prompt:

```text
Consolidate the planning docs after the packaging, docs, and CI slices all
merged. Make sure the landing README points at the right active plan and remove
stale claims.
```

Expected behavior:

- reconcile shared planning docs from landed work only
- correct stale claims that confuse scaffolded files with implemented endpoints
- make the landing README and execution README point to the canonical active
  plan
