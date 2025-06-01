# Migration Guide

Guide for upgrading between versions of the ReZEN Python client. This document covers breaking changes, new features, and migration steps for each major version.

---

## 🚀 Current Version: 1.5.4

The ReZEN Python client follows [Semantic Versioning](https://semver.org/). This guide helps you migrate between versions safely and efficiently.

---

## 📋 Migration Overview

### Version Support Policy

- **Major versions** (e.g., 1.x → 2.x): May contain breaking changes
- **Minor versions** (e.g., 1.4.x → 1.5.x): Backward compatible with new features
- **Patch versions** (e.g., 1.5.3 → 1.5.4): Bug fixes and security updates

### Before You Migrate

1. **Review the changelog** for your target version
2. **Test in a development environment** first
3. **Update your dependencies** and virtual environment
4. **Run your test suite** after upgrading
5. **Update your documentation** if needed

---

## 🔄 Version-Specific Migration Guides

### Migrating to 1.5.x from 1.4.x

**Release Date:** December 2024  
**Migration Difficulty:** 🟢 Easy (No breaking changes)

#### New Features

- Enhanced error handling with more specific exception types
- Improved pagination support for large datasets
- New directory API endpoints for vendor management
- Performance optimizations for network requests

#### Migration Steps

1. **Update the package**:
   ```bash
   pip install --upgrade rezen
   ```

2. **Update imports** (optional but recommended):
   ```python
   # Old way (still works)
   from rezen import RezenClient
   
   # New way (recommended for better error handling)
   from rezen import RezenClient
   from rezen.exceptions import (
       RezenError,
       AuthenticationError,
       ValidationError,
       NotFoundError,
       RateLimitError
   )
   ```

3. **Enhanced error handling** (optional):
   ```python
   # Before (generic exception handling)
   try:
       agents = client.agents.search_active_agents()
   except Exception as e:
       print(f"Error: {e}")
   
   # After (specific exception handling)
   try:
       agents = client.agents.search_active_agents()
   except AuthenticationError:
       print("Check your API key")
   except ValidationError as e:
       print(f"Invalid parameters: {e}")
   except RateLimitError:
       print("Rate limit exceeded")
   except RezenError as e:
       print(f"API error: {e}")
   ```

4. **New directory features** (optional):
   ```python
   # New directory API capabilities
   vendors = client.directory.search_vendors(
       page_number=0,
       page_size=20,
       roles=["TITLE_ESCROW", "LENDER"]
   )
   ```

#### Deprecations

- None in this version

#### Testing Your Migration

```python
import rezen

# Verify version
print(f"ReZEN client version: {rezen.__version__}")

# Test basic functionality
client = rezen.RezenClient()
try:
    teams = client.teams.search_teams(page_size=1)
    print("✅ Migration successful")
except Exception as e:
    print(f"❌ Migration issue: {e}")
```

### Migrating to 1.4.x from 1.3.x

**Release Date:** November 2024  
**Migration Difficulty:** 🟡 Moderate (Minor breaking changes)

#### Breaking Changes

1. **Agent search parameter changes**:
   ```python
   # Before (1.3.x)
   agents = client.agents.search_active_agents(state="CALIFORNIA")
   
   # After (1.4.x)
   agents = client.agents.search_active_agents(state_or_province=["CALIFORNIA"])
   ```

2. **Pagination parameter standardization**:
   ```python
   # Before (1.3.x)
   agents = client.agents.search_active_agents(page=0, limit=50)
   
   # After (1.4.x)
   agents = client.agents.search_active_agents(page_number=0, page_size=50)
   ```

#### Migration Steps

1. **Update search parameters**:
   ```python
   # Update all agent search calls
   # Old
   agents = client.agents.search_active_agents(
       state="CALIFORNIA",
       page=0,
       limit=100
   )
   
   # New
   agents = client.agents.search_active_agents(
       state_or_province=["CALIFORNIA"],
       page_number=0,
       page_size=100
   )
   ```

2. **Update pagination handling**:
   ```python
   # Update pagination logic
   def get_all_agents_old():
       page = 0
       while True:
           response = client.agents.search_active_agents(page=page, limit=100)
           # ... process response
           page += 1
   
   def get_all_agents_new():
       page_number = 0
       while True:
           response = client.agents.search_active_agents(
               page_number=page_number, 
               page_size=100
           )
           # ... process response
           page_number += 1
   ```

#### Automated Migration Script

```python
#!/usr/bin/env python3
"""
Automated migration script for ReZEN client 1.3.x → 1.4.x
"""

import re
import os
import glob

def migrate_file(filepath):
    """Migrate a single Python file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Track changes
    changes = []
    
    # Replace state parameter
    old_pattern = r'search_active_agents\([^)]*state="([^"]+)"'
    new_pattern = r'search_active_agents(\g<1>state_or_province=["\g<2>"]'
    if re.search(old_pattern, content):
        content = re.sub(old_pattern, new_pattern, content)
        changes.append("Updated state parameter to state_or_province")
    
    # Replace pagination parameters
    content = re.sub(r'\bpage=', 'page_number=', content)
    content = re.sub(r'\blimit=', 'page_size=', content)
    
    if changes:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"✅ Migrated {filepath}: {', '.join(changes)}")
    else:
        print(f"⏭️  No changes needed for {filepath}")

def main():
    """Run migration on all Python files in current directory."""
    python_files = glob.glob("**/*.py", recursive=True)
    
    for filepath in python_files:
        if 'venv' not in filepath and '.git' not in filepath:
            migrate_file(filepath)
    
    print("\n🎉 Migration complete!")
    print("Please review the changes and test your application.")

if __name__ == "__main__":
    main()
```

### Migrating to 1.3.x from 1.2.x

**Release Date:** October 2024  
**Migration Difficulty:** 🟢 Easy (No breaking changes)

#### New Features

- Transaction builder API enhancements
- Improved type hints and documentation
- New team management endpoints

#### Migration Steps

1. **Update package**: `pip install --upgrade rezen`
2. **Optional**: Use new transaction builder features
3. **Optional**: Leverage improved type hints for better IDE support

---

## 🛠️ Migration Tools & Scripts

### Version Compatibility Checker

```python
#!/usr/bin/env python3
"""
Check compatibility of your code with different ReZEN client versions.
"""

import ast
import sys
from typing import List, Dict, Any

class RezenCompatibilityChecker(ast.NodeVisitor):
    """AST visitor to check ReZEN API usage compatibility."""
    
    def __init__(self):
        self.issues = []
        self.rezen_imports = set()
    
    def visit_ImportFrom(self, node):
        """Track ReZEN imports."""
        if node.module and 'rezen' in node.module:
            for alias in node.names:
                self.rezen_imports.add(alias.name)
        self.generic_visit(node)
    
    def visit_Call(self, node):
        """Check method calls for compatibility issues."""
        # Check for deprecated parameters
        if hasattr(node.func, 'attr'):
            method_name = node.func.attr
            
            # Check for old pagination parameters
            if method_name == 'search_active_agents':
                for keyword in node.keywords:
                    if keyword.arg == 'page':
                        self.issues.append({
                            'line': node.lineno,
                            'issue': 'Deprecated parameter "page", use "page_number"',
                            'severity': 'warning'
                        })
                    elif keyword.arg == 'limit':
                        self.issues.append({
                            'line': node.lineno,
                            'issue': 'Deprecated parameter "limit", use "page_size"',
                            'severity': 'warning'
                        })
                    elif keyword.arg == 'state':
                        self.issues.append({
                            'line': node.lineno,
                            'issue': 'Deprecated parameter "state", use "state_or_province"',
                            'severity': 'error'
                        })
        
        self.generic_visit(node)

def check_file_compatibility(filepath: str) -> List[Dict[str, Any]]:
    """Check a Python file for ReZEN compatibility issues."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        tree = ast.parse(content)
        checker = RezenCompatibilityChecker()
        checker.visit(tree)
        
        return checker.issues
    except Exception as e:
        return [{'line': 0, 'issue': f'Parse error: {e}', 'severity': 'error'}]

def main():
    """Run compatibility check on specified files."""
    if len(sys.argv) < 2:
        print("Usage: python compatibility_checker.py <file1.py> [file2.py] ...")
        sys.exit(1)
    
    total_issues = 0
    
    for filepath in sys.argv[1:]:
        print(f"\n📁 Checking {filepath}...")
        issues = check_file_compatibility(filepath)
        
        if not issues:
            print("✅ No compatibility issues found")
        else:
            total_issues += len(issues)
            for issue in issues:
                severity_icon = "❌" if issue['severity'] == 'error' else "⚠️"
                print(f"{severity_icon} Line {issue['line']}: {issue['issue']}")
    
    print(f"\n📊 Summary: {total_issues} total issues found")
    
    if total_issues > 0:
        print("\n💡 Run the migration script to automatically fix common issues")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### Dependency Update Helper

```python
#!/usr/bin/env python3
"""
Helper script to update ReZEN client and related dependencies.
"""

import subprocess
import sys
import json
from typing import Dict, List

def run_command(command: List[str]) -> tuple:
    """Run a shell command and return output."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip()

def get_current_version() -> str:
    """Get currently installed ReZEN version."""
    success, output = run_command(['pip', 'show', 'rezen'])
    if success:
        for line in output.split('\n'):
            if line.startswith('Version:'):
                return line.split(':', 1)[1].strip()
    return "Not installed"

def get_latest_version() -> str:
    """Get latest available ReZEN version from PyPI."""
    success, output = run_command(['pip', 'index', 'versions', 'rezen'])
    if success:
        # Parse output to get latest version
        lines = output.split('\n')
        for line in lines:
            if 'Available versions:' in line:
                versions = line.split(':', 1)[1].strip().split(', ')
                return versions[0] if versions else "Unknown"
    return "Unknown"

def update_requirements_file(filename: str, new_version: str):
    """Update requirements file with new ReZEN version."""
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
        
        updated = False
        for i, line in enumerate(lines):
            if line.strip().startswith('rezen'):
                lines[i] = f"rezen=={new_version}\n"
                updated = True
                break
        
        if updated:
            with open(filename, 'w') as f:
                f.writelines(lines)
            print(f"✅ Updated {filename}")
        else:
            print(f"⚠️  ReZEN not found in {filename}")
    
    except FileNotFoundError:
        print(f"⚠️  {filename} not found")

def main():
    """Main update process."""
    print("🔄 ReZEN Client Update Helper")
    print("=" * 40)
    
    # Check current version
    current_version = get_current_version()
    print(f"Current version: {current_version}")
    
    # Check latest version
    latest_version = get_latest_version()
    print(f"Latest version: {latest_version}")
    
    if current_version == latest_version:
        print("✅ You're already on the latest version!")
        return
    
    # Confirm update
    response = input(f"\nUpdate from {current_version} to {latest_version}? (y/N): ")
    if response.lower() != 'y':
        print("Update cancelled")
        return
    
    # Perform update
    print("\n🔄 Updating ReZEN client...")
    success, output = run_command(['pip', 'install', '--upgrade', 'rezen'])
    
    if success:
        print("✅ ReZEN client updated successfully!")
        
        # Update requirements files
        print("\n📝 Updating requirements files...")
        update_requirements_file('requirements.txt', latest_version)
        update_requirements_file('requirements-dev.txt', latest_version)
        
        # Verify installation
        print("\n🔍 Verifying installation...")
        success, output = run_command(['python', '-c', 'import rezen; print(rezen.__version__)'])
        if success:
            print(f"✅ Verification successful: {output}")
        else:
            print(f"❌ Verification failed: {output}")
    else:
        print(f"❌ Update failed: {output}")
        sys.exit(1)
    
    print("\n🎉 Update complete!")
    print("💡 Don't forget to:")
    print("   - Run your test suite")
    print("   - Check the migration guide for any breaking changes")
    print("   - Update your documentation if needed")

if __name__ == "__main__":
    main()
```

---

## 🧪 Testing Your Migration

### Comprehensive Test Suite

```python
#!/usr/bin/env python3
"""
Comprehensive test suite for ReZEN client migration validation.
"""

import unittest
from unittest.mock import patch, MagicMock
from rezen import RezenClient
from rezen.exceptions import RezenError

class MigrationTestSuite(unittest.TestCase):
    """Test suite to validate ReZEN client functionality after migration."""
    
    def setUp(self):
        """Set up test client."""
        self.client = RezenClient()
    
    @patch('rezen.agents.AgentsClient.search_active_agents')
    def test_agent_search_compatibility(self, mock_search):
        """Test agent search with new parameter format."""
        mock_response = {
            "agents": [{"id": "test-agent", "firstName": "Test", "lastName": "Agent"}],
            "totalCount": 1
        }
        mock_search.return_value = mock_response
        
        # Test new parameter format
        result = self.client.agents.search_active_agents(
            state_or_province=["CALIFORNIA"],
            page_number=0,
            page_size=50
        )
        
        self.assertEqual(result, mock_response)
        mock_search.assert_called_once_with(
            state_or_province=["CALIFORNIA"],
            page_number=0,
            page_size=50
        )
    
    @patch('rezen.teams.TeamsClient.search_teams')
    def test_team_search_functionality(self, mock_search):
        """Test team search functionality."""
        mock_response = {
            "teams": [{"id": "test-team", "name": "Test Team"}],
            "totalCount": 1
        }
        mock_search.return_value = mock_response
        
        result = self.client.teams.search_teams(status="ACTIVE")
        
        self.assertEqual(result, mock_response)
        mock_search.assert_called_once_with(status="ACTIVE")
    
    def test_error_handling(self):
        """Test that error handling works correctly."""
        with patch.object(self.client.agents, 'search_active_agents') as mock_search:
            mock_search.side_effect = RezenError("Test error")
            
            with self.assertRaises(RezenError):
                self.client.agents.search_active_agents()
    
    def test_client_initialization(self):
        """Test that client initializes correctly."""
        self.assertIsNotNone(self.client)
        self.assertIsNotNone(self.client.agents)
        self.assertIsNotNone(self.client.teams)
        self.assertIsNotNone(self.client.transactions)
        self.assertIsNotNone(self.client.transaction_builder)
        self.assertIsNotNone(self.client.directory)

def run_migration_tests():
    """Run the migration test suite."""
    print("🧪 Running ReZEN Migration Test Suite")
    print("=" * 40)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(MigrationTestSuite)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Report results
    if result.wasSuccessful():
        print("\n✅ All migration tests passed!")
        print("Your ReZEN client migration was successful.")
    else:
        print(f"\n❌ {len(result.failures)} test(s) failed")
        print(f"❌ {len(result.errors)} error(s) occurred")
        print("Please review the migration guide and fix any issues.")
        
        return False
    
    return True

if __name__ == "__main__":
    success = run_migration_tests()
    exit(0 if success else 1)
```

---

## 📚 Additional Resources

### Migration Checklist

- [ ] **Backup your current code** before starting migration
- [ ] **Review the changelog** for your target version
- [ ] **Update your virtual environment** and dependencies
- [ ] **Run the compatibility checker** on your codebase
- [ ] **Apply automated migration scripts** if available
- [ ] **Update your code** for any breaking changes
- [ ] **Run your test suite** to verify functionality
- [ ] **Test in a staging environment** before production
- [ ] **Update your documentation** and deployment scripts
- [ ] **Monitor your application** after deployment

### Getting Help

If you encounter issues during migration:

1. **Check the [FAQ](faq.md)** for common migration questions
2. **Review the [Troubleshooting Guide](troubleshooting.md)** for debugging tips
3. **Search [GitHub Issues](https://github.com/theperrygroup/rezen/issues)** for similar problems
4. **Open a new issue** with your migration details if needed

### Version History

| Version | Release Date | Migration Difficulty | Key Changes |
|---------|--------------|---------------------|-------------|
| 1.5.4   | Dec 2024     | 🟢 Easy            | Enhanced error handling, directory API |
| 1.4.0   | Nov 2024     | 🟡 Moderate        | Parameter standardization |
| 1.3.0   | Oct 2024     | 🟢 Easy            | Transaction builder enhancements |
| 1.2.0   | Sep 2024     | 🟢 Easy            | Type hints improvements |
| 1.1.0   | Aug 2024     | 🟡 Moderate        | API restructuring |
| 1.0.0   | Jul 2024     | 🔴 Major           | Initial stable release |

---

**Need help with migration?** Check our [FAQ](faq.md) or [open an issue](https://github.com/theperrygroup/rezen/issues) on GitHub.