---
name: python-api-client-planning
description: Plans and scaffolds typed Python API client libraries from API docs URLs, local `docs/api/` folders, and OpenAPI or Swagger artifacts. Use when rebuilding or bootstrapping a Python API client repo with multi-phase planning, repo-local Cursor rules, package structure, tests and coverage, MkDocs docs, GitHub Actions, release automation, and examples.
---
# Python API Client Planning

Use this skill when the goal is to recreate a ReZEN-style Python API client
repository from documentation, not to implement every endpoint in one pass.

## Read First

- Read `reference.md` before creating or updating anything.
- If the target repo already has `docs/planning/` for the initiative, read the
  landing README, artifact index, execution docs, and focused trackers before
  editing.
- If the repo already has `.cursor/rules/`, read the existing rules before
  generating new ones so you extend the current contract instead of forking it.

## Default Scope

- Python library first.
- Default deliverable: a full planning tree, repo-local rules, and starter
  scaffold.
- Default non-goal: full endpoint implementation in the same pass unless the
  user explicitly asks for it.

## API Source Audit

Use this precedence order:

1. Explicit API docs URL from the user.
2. Checked-in `docs/api/`.
3. Checked-in OpenAPI or Swagger files and schema folders.
4. Endpoint task docs or similar backlog artifacts.

Before planning or scaffolding, capture one source-of-truth matrix that records:

- authentication and environment rules
- base URLs and versioning
- resource groups and endpoint inventory
- request and response schemas, enums, and uploads
- pagination, rate limits, webhooks, and error models
- contradictions, gaps, or missing examples

If higher-precedence and lower-precedence sources disagree, prefer the
higher-precedence source and record the gap in the planning tree before coding.

## Modes

Use the same four modes as the multi-phase planning skill:

- `scaffold`: create or update the full planning root, `.cursor/rules/`, and
  starter repo scaffold.
- `extend`: add or deepen an active plan, tracker, phase proof, or scaffold
  slice.
- `refresh`: synchronize planning docs and repo rules after checked-in work
  changes the truth.
- `consolidate`: reconcile the shared planning docs after multiple slices land.

If a request includes first-time planning plus scaffold creation, use
`scaffold`.

If it adds a new phase and also needs status sync, run `extend` first and
`refresh` second in the same pass.

## Required Workflow

### Scaffold

1. Derive the initiative slug, package name, and current repo baseline.
2. Run the API source audit and create the source-of-truth foundation docs.
3. Create the full `docs/planning/<initiative-slug>/` tree.
4. Generate or update repo-local `.cursor/rules/` using the templates in
   `reference.md`.
5. Scaffold the Python library baseline: package root, tests, docs, examples,
   automation, and supporting config files.
6. Validate the scaffold and leave endpoint implementation as planned work
   unless the user requested more.

### Extend

1. Read the existing planning root, active plan, current ledger, and relevant
   rules.
2. Prefer extending the canonical active plan over creating competing siblings.
3. Add or update scaffold slices only when the new phase materially changes
   package, docs, tests, or automation structure.

### Refresh

1. Inspect checked-in code, docs, workflows, and rules before changing status
   language.
2. Update phase proof, focused trackers, readiness overview, execution ledger,
   and rule docs in that order.
3. Keep the roadmap untouched unless the baseline dependency order changed.

### Consolidate

1. Reconcile shared planning docs and rules from landed work only.
2. Remove stale claims that treat scaffolded files as implemented endpoints.
3. Make the landing README and execution README point to the current canonical
   active plan.

## Guardrails

- Do not silently overwrite existing package metadata, workflows, or rules.
  Extend them or record the gap.
- Do not mark API coverage complete until endpoint inventory, tests, docs, and
  coverage prove it.
- Do not treat starter scaffold creation as endpoint completion.
- Keep rules, tests, docs, and examples synchronized with the planning tree.
- Use Google-style docstrings and thorough type hints in generated Python.
- Record intentional deviations instead of quietly drifting from the baseline.

## Output Requirements

For every run, report:

- the chosen API source inputs and precedence resolution
- the planning root that owns the work
- rules created or updated
- scaffold files created or updated
- what was intentionally deferred to later phases
- tests or validation commands run when files changed

## Additional Resources

- For planning templates, rule templates, scaffold contracts, and validation
  commands, see [reference.md](reference.md).
- For example invocations, see [examples.md](examples.md).
