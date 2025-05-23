#!/usr/bin/env python3
"""Version bumping utility for ReZEN API package.

This script helps maintain version consistency across files and creates proper tags for releases.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Tuple


def get_current_version() -> str:
    """Get current version from pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text()
    
    match = re.search(r'^version = "([^"]+)"', content, re.MULTILINE)
    if not match:
        raise ValueError("Could not find version in pyproject.toml")
    
    return match.group(1)


def bump_version(current: str, bump_type: str) -> str:
    """Bump version based on semantic versioning."""
    major, minor, patch = map(int, current.split('.'))
    
    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")


def update_version_in_file(file_path: Path, old_version: str, new_version: str) -> None:
    """Update version in a specific file."""
    content = file_path.read_text()
    
    if file_path.name == "pyproject.toml":
        content = re.sub(
            rf'^version = "{re.escape(old_version)}"',
            f'version = "{new_version}"',
            content,
            flags=re.MULTILINE
        )
    elif file_path.name == "__init__.py":
        content = re.sub(
            rf'^__version__ = "{re.escape(old_version)}"',
            f'__version__ = "{new_version}"',
            content,
            flags=re.MULTILINE
        )
    
    file_path.write_text(content)
    print(f"✅ Updated {file_path}")


def run_command(cmd: list) -> Tuple[int, str]:
    """Run a shell command and return exit code and output."""
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            check=False
        )
        return result.returncode, result.stdout + result.stderr
    except Exception as e:
        return 1, str(e)


def main() -> None:
    """Main version bumping logic."""
    parser = argparse.ArgumentParser(description="Bump ReZEN API package version")
    parser.add_argument(
        "bump_type", 
        choices=["major", "minor", "patch"],
        help="Type of version bump"
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true",
        help="Show what would be done without making changes"
    )
    parser.add_argument(
        "--tag", 
        action="store_true",
        help="Create git tag after version bump"
    )
    parser.add_argument(
        "--push", 
        action="store_true",
        help="Push changes and tags to remote (implies --tag)"
    )
    
    args = parser.parse_args()
    
    # Get current version
    try:
        current_version = get_current_version()
        print(f"📋 Current version: {current_version}")
    except Exception as e:
        print(f"❌ Error getting current version: {e}")
        sys.exit(1)
    
    # Calculate new version
    new_version = bump_version(current_version, args.bump_type)
    print(f"🎯 New version: {new_version}")
    
    if args.dry_run:
        print("🔍 DRY RUN - No changes will be made")
        print(f"Would update:")
        print(f"  - pyproject.toml: {current_version} → {new_version}")
        print(f"  - rezen/__init__.py: {current_version} → {new_version}")
        if args.tag or args.push:
            print(f"  - Git tag: v{new_version}")
        if args.push:
            print(f"  - Push to remote")
        return
    
    # Update version files
    files_to_update = [
        Path("pyproject.toml"),
        Path("rezen/__init__.py")
    ]
    
    for file_path in files_to_update:
        if not file_path.exists():
            print(f"⚠️  File not found: {file_path}")
            continue
        
        try:
            update_version_in_file(file_path, current_version, new_version)
        except Exception as e:
            print(f"❌ Error updating {file_path}: {e}")
            sys.exit(1)
    
    # Git operations
    if args.tag or args.push:
        # Stage changes
        exit_code, output = run_command(["git", "add", "pyproject.toml", "rezen/__init__.py"])
        if exit_code != 0:
            print(f"❌ Error staging files: {output}")
            sys.exit(1)
        
        # Commit changes
        commit_msg = f"Bump version to {new_version}"
        exit_code, output = run_command(["git", "commit", "-m", commit_msg])
        if exit_code != 0:
            print(f"❌ Error committing changes: {output}")
            sys.exit(1)
        
        print(f"✅ Committed version bump")
        
        # Create tag
        tag_name = f"v{new_version}"
        exit_code, output = run_command(["git", "tag", "-a", tag_name, "-m", f"Release {tag_name}"])
        if exit_code != 0:
            print(f"❌ Error creating tag: {output}")
            sys.exit(1)
        
        print(f"✅ Created tag: {tag_name}")
        
        # Push to remote
        if args.push:
            # Push commits
            exit_code, output = run_command(["git", "push"])
            if exit_code != 0:
                print(f"❌ Error pushing commits: {output}")
                sys.exit(1)
            
            # Push tags
            exit_code, output = run_command(["git", "push", "--tags"])
            if exit_code != 0:
                print(f"❌ Error pushing tags: {output}")
                sys.exit(1)
            
            print(f"✅ Pushed changes and tags to remote")
            print(f"🚀 Release workflow should start automatically!")
    
    print(f"\n🎉 Version bumped successfully!")
    print(f"📦 New version: {new_version}")
    
    if not (args.tag or args.push):
        print(f"\n💡 Next steps:")
        print(f"   git add .")
        print(f"   git commit -m 'Bump version to {new_version}'")
        print(f"   git tag -a v{new_version} -m 'Release v{new_version}'")
        print(f"   git push && git push --tags")


if __name__ == "__main__":
    main() 