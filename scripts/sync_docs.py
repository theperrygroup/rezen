#!/usr/bin/env python3
"""
Documentation Sync Script for ReZEN Python Client

This script helps maintain consistency between README.md, docs/index.md,
and shared content files. It validates that all includes are working
and provides tools for updating shared content.

Usage:
    python scripts/sync_docs.py validate    # Validate includes work
    python scripts/sync_docs.py build       # Build docs and validate
    python scripts/sync_docs.py update      # Update shared content from template
"""

import os
import re
import subprocess
import sys
from pathlib import Path


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


def validate_includes() -> bool:
    """Validate that all include files exist and are referenced correctly."""
    project_root = get_project_root()
    includes_dir = project_root / "docs" / "_includes"

    if not includes_dir.exists():
        print("❌ _includes directory does not exist")
        return False

    # Find all include files
    include_files = list(includes_dir.glob("*.md"))
    if not include_files:
        print("❌ No include files found in _includes/")
        return False

    print(f"✅ Found {len(include_files)} include files:")
    for include_file in include_files:
        print(f"   - {include_file.name}")

    # Check if includes are referenced in README and docs
    readme_path = project_root / "README.md"
    index_path = project_root / "docs" / "index.md"

    include_pattern = re.compile(r"\{!.*?!\}")

    # Check README.md
    if readme_path.exists():
        readme_content = readme_path.read_text()
        readme_includes = include_pattern.findall(readme_content)
        print(f"✅ README.md uses {len(readme_includes)} includes")
    else:
        print("❌ README.md not found")
        return False

    # Check docs/index.md
    if index_path.exists():
        index_content = index_path.read_text()
        index_includes = include_pattern.findall(index_content)
        print(f"✅ docs/index.md uses {len(index_includes)} includes")
    else:
        print("❌ docs/index.md not found")
        return False

    return True


def build_docs() -> bool:
    """Build the documentation and check for errors."""
    project_root = get_project_root()
    os.chdir(project_root)

    try:
        # Try building docs (without strict mode for includes)
        result = subprocess.run(
            ["mkdocs", "build", "--clean"], capture_output=True, text=True
        )

        if result.returncode == 0:
            print("✅ Documentation built successfully")
            return True
        else:
            print("❌ Documentation build failed:")
            print(result.stderr)
            return False

    except FileNotFoundError:
        print("❌ mkdocs not found. Please install with: pip install mkdocs")
        return False


def update_api_coverage() -> None:
    """Update API coverage based on actual implementation."""
    project_root = get_project_root()
    rezen_dir = project_root / "rezen"

    if not rezen_dir.exists():
        print("❌ rezen/ directory not found")
        return

    # Count endpoints in each module
    modules = {
        "Transaction Builder": "transaction_builder.py",
        "Transactions": "transactions.py",
        "Agents": "agents.py",
        "Teams": "teams.py",
        "Directory": "directory.py",
    }

    coverage_data = {}
    total_endpoints = 0

    for module_name, filename in modules.items():
        module_path = rezen_dir / filename
        if module_path.exists():
            content = module_path.read_text()
            # Count methods that start with def and are not private
            methods = re.findall(r"\n    def ([a-zA-Z][a-zA-Z0-9_]*)\(", content)
            # Filter out common base methods
            exclude_methods = {"__init__", "get", "post", "_request"}
            endpoint_count = len([m for m in methods if m not in exclude_methods])
            coverage_data[module_name] = endpoint_count
            total_endpoints += endpoint_count
            print(f"✅ {module_name}: {endpoint_count} endpoints")
        else:
            print(f"❌ {filename} not found")
            coverage_data[module_name] = 0

    # Update the API coverage include file
    coverage_file = project_root / "docs" / "_includes" / "api-coverage.md"

    coverage_content = "| **API Section** | **Endpoints** | **Status** |\n"
    coverage_content += "|-----------------|---------------|------------|\n"

    for module_name, count in coverage_data.items():
        status = "✅ Complete" if count > 0 else "❌ Incomplete"
        coverage_content += f"| {module_name} | {count} endpoints | {status} |\n"

    coverage_content += (
        f"| **Total** | **{total_endpoints} endpoints** | **✅ Complete** |"
    )

    coverage_file.write_text(coverage_content)
    print(f"✅ Updated API coverage: {total_endpoints} total endpoints")


def main() -> None:
    """Main script function."""
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == "validate":
        success = validate_includes()
        sys.exit(0 if success else 1)

    elif command == "build":
        validate_success = validate_includes()
        build_success = build_docs()
        sys.exit(0 if validate_success and build_success else 1)

    elif command == "update":
        update_api_coverage()
        print("✅ Updated shared content")

    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
