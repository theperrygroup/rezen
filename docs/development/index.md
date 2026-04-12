# Development Guide

This section covers the local development workflow, contributor expectations, and deployment automation for the ReZEN Python client.

## At a Glance

- The package requires Python 3.8 or newer.
- CI currently exercises Python 3.8 through 3.12.
- The contributor setup that best matches CI is `python -m pip install -e ".[dev]"`.
- Local docs work also needs `python -m pip install -r docs/requirements.txt`.
- This repository does not currently ship a `.pre-commit-config.yaml`; run the quality commands directly.

## Local Setup

```bash
git clone https://github.com/theperrygroup/rezen.git
cd rezen
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m pip install -r docs/requirements.txt
```

## Common Checks

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

CI adds security scans and configuration validation on top of those local checks.

## Next Reads

<div class="grid cards" markdown>

-   **Contributing**

    ---

    Branching, local verification, pull request expectations, and style-guide ownership.

    [:octicons-arrow-right-24: Open the guide](contributing.md)

-   **Deployment**

    ---

    What `ci.yml` and `unified-deployment.yml` actually do, including docs and release automation.

    [:octicons-arrow-right-24: Open the guide](deployment.md)

-   **Documentation Style Guide**

    ---

    Writing conventions for Markdown pages, examples, navigation, and MkDocs-specific content.

    [:octicons-arrow-right-24: Open the guide](../STYLE_GUIDE.md)

-   **Repository Style Guide**

    ---

    Canonical code-style guidance for type hints, docstrings, error handling, and project conventions.

    [:octicons-arrow-right-24: View on GitHub](https://github.com/theperrygroup/rezen/blob/main/STYLE_GUIDE.md)

</div>
