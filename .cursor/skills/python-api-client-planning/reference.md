# Python API Client Planning Reference

Use this reference when creating or extending a typed Python API client
repository from documentation. This reference is self-contained so the skill can
be copied into another repository without depending on project-specific planning
files.

## Default Assumptions

- The target is a Python library first, not a web app or CLI-first project.
- Default to a full scaffold because package structure, tests, docs, workflows,
  and repo rules cross durable ownership boundaries.
- Treat `docs/planning/<initiative-slug>/` as docs-only. Runtime code, tests,
  docs site files, workflows, and rules belong outside the planning tree.
- Prefer `pyproject.toml` as the canonical place for package metadata and tool
  configuration unless the planning docs record an intentional exception.
- Generated Python should use Google-style docstrings, strong type hints, and a
  shipped `py.typed` marker.
- The default quality baseline is Black, isort, flake8, mypy, pytest with
  coverage, `build`, `twine`, MkDocs Material with `mkdocstrings`, GitHub
  Actions, security automation, and Dependabot.

## Naming And Path Rules

- Initiative roots use stable kebab-case slugs:
  `docs/planning/<initiative-slug>/`
- Package names use snake_case and should align with the import package:
  `<package_name>/`
- If the project name uses hyphens, convert them to underscores for the import
  package name and keep the relationship explicit in the planning docs.
- Keep version data in exactly two places by default:
  `pyproject.toml` and `<package_name>/__init__.py`
- Use one canonical active plan name for first-time scaffolds:
  `execution/api-client-bootstrap-plan.md`
- Use phase proof names like:
  `execution/api_client_PHASE_00_source_audit.md`
  `execution/api_client_PHASE_01_foundation.md`
- Repo-local rules live under `.cursor/rules/`
- Keep one planning root per client workstream. Extend the existing tree instead
  of creating near-duplicate roots.

## API Source Discovery Order

Resolve the source of truth in this order:

1. An explicit API docs URL from the user.
2. Checked-in `docs/api/`.
3. Checked-in OpenAPI or Swagger files, schema folders, or endpoint maps.
4. Endpoint backlog docs such as `tasks/`, checklists, or hand-written endpoint
   notes.

When searching locally, look for patterns like:

- `docs/api/**`
- `openapi/**`
- `swagger*.json`
- `swagger*.yaml`
- `swagger*.yml`
- `openapi*.json`
- `openapi*.yaml`
- `openapi*.yml`
- `**/endpoints.json`
- `tasks/**/*.md`

If a URL is the highest-precedence source:

- Fetch the landing docs page first.
- Look for linked OpenAPI or Swagger files before inferring structure from prose
  alone.
- Record any rate limits, auth rules, pagination rules, upload behavior, and
  error shapes that appear only in prose docs.

If local docs are the highest-precedence source:

- Read `docs/api/index.md` first if it exists.
- Inventory resource pages before reading deeper pages.
- Use OpenAPI or schema files as a validator for the prose docs, not as a
  silent replacement when the docs disagree.

If multiple sources conflict:

- Prefer the higher-precedence source.
- Record the contradiction in the planning tree.
- Keep implementation work blocked on unresolved contract questions instead of
  inventing behavior.

## Required Source Audit Outputs

Always create or update these foundation docs during scaffold mode.

### `foundation/api-source-of-truth.md`

Use this structure:

```markdown
# API Source Of Truth

## Source Priority

1. <highest-priority source>
2. <next source>

## Inputs Used

| Source | Path or URL | Status | Why it matters |
| --- | --- | --- | --- |
| ... | ... | ... | ... |

## Base Contract

| Area | Current answer | Canonical source |
| --- | --- | --- |
| Base URL | ... | ... |
| Authentication | ... | ... |
| Versioning | ... | ... |
| Pagination | ... | ... |
| Errors | ... | ... |
| Rate limits | ... | ... |

## Resource Inventory

| Resource group | Coverage status | Notes |
| --- | --- | --- |
| ... | ... | ... |

## Contradictions And Gaps

- ...

## Follow-Up Before Implementation

- ...
```

### `foundation/source-of-truth-matrix.md`

Use this structure:

```markdown
# Source Of Truth Matrix

| Topic | Canonical source | Secondary source | Confidence | Follow-up |
| --- | --- | --- | --- | --- |
| Authentication | ... | ... | High | None |
| Resource grouping | ... | ... | Medium | Confirm naming |
| Error contract | ... | ... | Low | Needs live example |
```

The audit must cover:

- authentication and environment setup
- base URLs and versioning
- resource groups and endpoint inventory
- request and response schemas
- enums and shared types
- pagination, sorting, filtering, and search behavior
- uploads, downloads, and content types
- error models and retry guidance
- rate limits or throttling
- webhook or async callback behavior if present
- missing examples or unresolved contradictions

## Default Planning Tree

Default to this full scaffold:

```text
docs/planning/<initiative-slug>/
  README.md
  ARTIFACT_PATH_INDEX.md
  foundation/
    README.md
    source-of-truth-matrix.md
    api-source-of-truth.md
    package-and-versioning-adr.md
    rules-and-ownership-adr.md
  trackers/
    README.md
    readiness-overview.md
    endpoint-inventory-readiness.md
    coverage-and-tests-readiness.md
    docs-parity-readiness.md
    workflow-release-readiness.md
  execution/
    README.md
    roadmap.md
    execution-plan.md
    api-client-bootstrap-plan.md
    api_client_PHASE_00_source_audit.md
    api_client_PHASE_01_foundation.md
    api_client_PHASE_02_endpoint_inventory.md
    api_client_PHASE_03_tests_and_coverage.md
    api_client_PHASE_04_docs_and_examples.md
    api_client_PHASE_05_workflows_and_release.md
    api_client_PHASE_06_parity_audit.md
```

Always create:

- `README.md`
- `ARTIFACT_PATH_INDEX.md`
- `foundation/README.md`
- `foundation/source-of-truth-matrix.md`
- `foundation/api-source-of-truth.md`
- `trackers/README.md`
- `trackers/readiness-overview.md`
- `execution/README.md`
- `execution/execution-plan.md`
- `execution/roadmap.md`
- `execution/api-client-bootstrap-plan.md`

Create the phase proof files immediately when the first scaffold needs durable
evidence for each phase. If the project is still very early, keep the proof
files short and let the execution ledger stay canonical for live status.

## Planning Doc Contracts

### `README.md`

The landing README should define:

- that the planning tree is docs-only
- the current status snapshot
- the fastest reality-check docs
- document precedence
- update order
- the canonical active plan doc

### `ARTIFACT_PATH_INDEX.md`

The path index should list the canonical home for:

- the planning root
- the rules directory
- the package directory
- the tests directory
- the docs site
- the examples directory
- workflow files
- dependency automation
- requirements files if they exist

Do not use this file as a live status ledger.

### `execution/execution-plan.md`

The execution plan is the live checked-in ledger. It should record:

- what is already scaffolded
- what is only planned
- the highest-risk remaining surface
- current blockers
- the current work queue

### `execution/roadmap.md`

The roadmap is the baseline dependency map. It should:

- list the ordered phases
- state why each phase exists
- name the exact files or directories affected
- identify acceptance criteria
- describe what breaks if the phase is skipped

### `execution/api-client-bootstrap-plan.md`

Use this as the canonical active plan for first-time scaffolds. At minimum it
should include:

```markdown
# API Client Bootstrap Plan

## Goal

- Recreate a typed Python API client baseline from the available API docs.

## Current Focus

- <current phase>

## Ordered Phases

### Phase 0 - Source Audit
- Inputs:
- Deliverables:
- Exit criteria:

### Phase 1 - Foundation And Packaging
- Inputs:
- Deliverables:
- Exit criteria:

### Phase 2 - Endpoint Inventory And Models
- Inputs:
- Deliverables:
- Exit criteria:

### Phase 3 - Tests And Coverage
- Inputs:
- Deliverables:
- Exit criteria:

### Phase 4 - Docs And Examples
- Inputs:
- Deliverables:
- Exit criteria:

### Phase 5 - Workflows And Release
- Inputs:
- Deliverables:
- Exit criteria:

### Phase 6 - Parity Audit
- Inputs:
- Deliverables:
- Exit criteria:
```

### Focused Trackers

Use focused trackers to keep the current truth honest:

- `endpoint-inventory-readiness.md`: resource groups, endpoint coverage, model
  mapping, auth understanding
- `coverage-and-tests-readiness.md`: pytest setup, fixture strategy, mocking,
  coverage goals, missing suites
- `docs-parity-readiness.md`: README, MkDocs nav, API pages, examples,
  troubleshooting, contributor docs
- `workflow-release-readiness.md`: CI, release, docs deploy, security, and
  dependency automation

## Default Phase Sequence

Use this phased sequence unless the target repo already has a stronger local
contract.

### Phase 0 - Source Audit

Goal: establish one honest API source of truth.

Deliverables:

- `foundation/api-source-of-truth.md`
- `foundation/source-of-truth-matrix.md`
- a first-pass resource inventory
- a contradiction list that blocks implementation when needed

### Phase 1 - Foundation And Packaging

Goal: make package identity, metadata, and runtime primitives coherent.

Typical outputs:

- `pyproject.toml`
- `<package_name>/__init__.py`
- `<package_name>/client.py`
- `<package_name>/base_client.py`
- `<package_name>/exceptions.py`
- `<package_name>/py.typed`
- `foundation/package-and-versioning-adr.md`

Questions to settle:

- package name versus distribution name
- version source of truth
- dependency source of truth
- auth and environment handling
- shared HTTP client behavior

### Phase 2 - Endpoint Inventory And Models

Goal: decide how the API surface maps onto modules, clients, and models before
claiming implementation progress.

Typical outputs:

- one module map per resource group
- placeholder service modules or client classes
- shared request and response model strategy
- `trackers/endpoint-inventory-readiness.md`
- `execution/api_client_PHASE_02_endpoint_inventory.md`

Questions to settle:

- resource grouping
- pagination and filtering patterns
- upload and download endpoints
- shared schemas and enums
- naming differences between API fields and Python methods

### Phase 3 - Tests And Coverage

Goal: define a full test harness and honest coverage story.

Typical outputs:

- `tests/__init__.py`
- `tests/conftest.py`
- `tests/test_client.py`
- `tests/test_base_client.py`
- `tests/test_exceptions.py`
- one test module per resource group
- coverage config in `pyproject.toml`
- `trackers/coverage-and-tests-readiness.md`

Coverage expectations:

- use pytest with coverage against `<package_name>`
- keep unit tests near full API surface expectations
- do not claim 100 percent coverage until the reports and CI prove it

### Phase 4 - Docs And Examples

Goal: make the published docs truthful, navigable, and aligned with the code.

Typical outputs:

- `README.md`
- `mkdocs.yml`
- `docs/index.md`
- `docs/getting-started/`
- `docs/api/`
- `docs/reference/`
- `docs/development/`
- `docs/requirements.txt`
- `examples/`
- `trackers/docs-parity-readiness.md`

Docs expectations:

- MkDocs Material plus `mkdocstrings`
- Google docstring rendering
- API docs pages per resource group
- contributor and deployment guidance that matches the workflows

### Phase 5 - Workflows And Release

Goal: bring CI, release, docs deploy, security, and dependency automation into
one coherent baseline.

Typical outputs:

- `.github/workflows/ci.yml`
- `.github/workflows/unified-deployment.yml`
- `.github/workflows/security-audit.yml`
- `.github/workflows/docs.yml`
- `.github/workflows/release.yml`
- `.github/dependabot.yml`
- `trackers/workflow-release-readiness.md`

Workflow expectations:

- formatting, import order, lint, typing, tests, and build checks
- docs built with `mkdocs build --strict`
- version parity between tags, `pyproject.toml`, and `__init__.py`
- scheduled security and dependency automation

### Phase 6 - Parity Audit

Goal: compare the target repo against the intended baseline and record the
remaining gaps honestly.

Typical outputs:

- updated readiness trackers
- execution ledger summary
- a short gap map inside the planning tree
- explicit follow-up phases for anything intentionally deferred

## Repo Rule Templates

If the target repo already has a matching rule, update it instead of creating a
duplicate. Replace placeholders when generating the final files.

### Optional `styleguide.mdc`

```markdown
---
description:
globs:
alwaysApply: true
---
Always check `./STYLE_GUIDE.md` before coding.

If the repo also keeps `docs/STYLE_GUIDE.md`, treat the root guide as canonical
for code conventions and the docs guide as the companion for prose structure.
```

### `api-source-truth.mdc`

```markdown
---
description: Source-of-truth rules for the API client project.
globs:
alwaysApply: true
---
Before implementing or changing API behavior, read
`docs/planning/<initiative-slug>/foundation/api-source-of-truth.md` and
`docs/planning/<initiative-slug>/foundation/source-of-truth-matrix.md`.

Prefer sources in this order:
1. explicit API docs URL from the user
2. checked-in `docs/api/`
3. checked-in OpenAPI or Swagger artifacts
4. endpoint task docs or backlog notes

If the sources disagree, record the contradiction in the planning tree before
coding.
```

### `api-client-implementation.mdc`

```markdown
---
description: Implementation rules for the Python API client project.
globs:
alwaysApply: true
---
Implement runtime code under `./<package_name>/` and group endpoints by resource
or service boundary.

Use Google-style docstrings and thorough type hints for generated Python.

Every endpoint or client change must update:
- tests under `./tests/`
- docs under `./docs/`
- examples under `./examples/` when user-facing usage changes
- the owning planning docs under `docs/planning/<initiative-slug>/`

Do not mark an endpoint complete until code, tests, docs, and status docs all
land.
```

### `docs-tests-sync.mdc`

```markdown
---
description: Keep docs, tests, and examples aligned with the client surface.
globs:
alwaysApply: true
---
When scaffolding or changing the client surface, keep `README.md`, `docs/`,
`examples/`, and `tests/` synchronized with the same commands and supported
Python versions.

Use pytest with coverage on `<package_name>`.

Docs must build with `mkdocs build --strict` before the work is considered
ready.
```

### `release-quality-contract.mdc`

```markdown
---
description: Quality and release rules for the Python API client project.
globs:
alwaysApply: true
---
Before changing CI or release behavior, keep `pyproject.toml`,
`<package_name>/__init__.py`, and the release workflow aligned on versioning.

CI must cover formatting, import order, lint, typing, tests, build, docs strict
build, and security or dependency automation.

Use Dependabot as the default dependency automation tool unless the planning
docs record an intentional exception.
```

## Starter Scaffold Contract

Use this as the baseline repository shape:

```text
<repo>/
  <package_name>/
    __init__.py
    client.py
    base_client.py
    exceptions.py
    py.typed
    <resource_module>.py
  tests/
    __init__.py
    conftest.py
    test_client.py
    test_base_client.py
    test_exceptions.py
    test_<resource_module>.py
  docs/
    index.md
    getting-started/
    api/
    reference/
    development/
    requirements.txt
  examples/
    quickstart.py
    <workflow>_example.py
  docs_extensions/
    __init__.py
    collapsible_tables.py
  tools/
    sync_security_dependency_versions.py
  .github/workflows/
    ci.yml
    unified-deployment.yml
    security-audit.yml
    docs.yml
    release.yml
  .github/dependabot.yml
  .cursor/rules/
  README.md
  STYLE_GUIDE.md
  mkdocs.yml
  pyproject.toml
  MANIFEST.in
```

### Key File Contracts

| File or directory | Minimum contract |
| --- | --- |
| `pyproject.toml` | PEP 621 metadata, optional dev extras, package discovery, tool config for Black, isort, mypy, pytest, coverage, pydocstyle, and flake8, plus `py.typed` package data |
| `<package_name>/__init__.py` | exported client surface and `__version__` |
| `<package_name>/client.py` | top-level client that wires subclients or service groups |
| `<package_name>/base_client.py` | shared HTTP session, auth handling, retries, request helpers |
| `<package_name>/exceptions.py` | project-specific exception hierarchy |
| `tests/` | pytest suite with base tests plus one module per resource group |
| `README.md` | install, quickstart, API coverage snapshot, docs links, development commands |
| `mkdocs.yml` | Material theme, `mkdocstrings`, Google docstring rendering, getting-started, guides, API, reference, and development nav |
| `docs/requirements.txt` | docs toolchain needed for strict local builds |
| `docs/api/` | one index page plus one page per resource group or major surface |
| `examples/` | at least one quickstart and one workflow example |
| `.github/workflows/ci.yml` | code quality job, test matrix, build job |
| `.github/workflows/unified-deployment.yml` | release, docs deploy, version checks, packaging checks |
| `.github/workflows/security-audit.yml` | scheduled dependency audit and PR creation |
| `.github/dependabot.yml` | root pip, docs pip, and GitHub Actions updates |
| `MANIFEST.in` | include README, LICENSE, relevant requirements, package data, and docs markdown when shipping them is intentional |

### Optional Surfaces

- `docs_extensions/`: keep this when the docs plan needs local Markdown
  extensions or custom MkDocs behavior.
- `tools/`: keep this when the repo needs maintenance scripts such as dependency
  sync helpers.
- `requirements.txt` and `requirements-dev.txt`: use them only when the planning
  docs also explain the source-of-truth relationship with `pyproject.toml`.

## Validation Session

When the scaffold changes code or config, use a validation session like this,
with `<package_name>` replaced:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m pip install -r docs/requirements.txt
python -m pip install build twine
black --check --diff --line-length=88 .
isort --check-only --diff --profile=black --line-length=88 .
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics
mypy <package_name>/ --strict --ignore-missing-imports
pytest --cov=<package_name> --cov-report=xml --cov-report=term-missing
mkdocs build --strict
python -m build
python -m twine check dist/*
```

If the repo intentionally diverges from this baseline, document the exception in
the planning tree before adjusting the command set.

## Not Done By Default

Do not imply these are complete just because the scaffold exists:

- full endpoint implementation
- complete API coverage
- 100 percent test coverage
- publication to PyPI or a package registry
- live docs deployment
- deletion of legacy workflows, rules, or manifests without a documented reason
- invented API behavior that the source audit did not support
