# Release Guide

This document explains how to release new versions of the ReZEN API package to PyPI and GitHub.

## 🎯 Quick Release Process

### Option 1: Automated (Recommended)

```bash
# Bump version and create release in one command
python scripts/bump_version.py patch --push

# For minor version bump
python scripts/bump_version.py minor --push

# For major version bump  
python scripts/bump_version.py major --push
```

### Option 2: Manual

```bash
# 1. Update version numbers manually in:
#    - pyproject.toml
#    - rezen/__init__.py

# 2. Create commit and tag
git add .
git commit -m "Bump version to 1.0.2"
git tag -a v1.0.2 -m "Release v1.0.2"

# 3. Push to trigger release
git push && git push --tags
```

## 📋 Setup Requirements

### 1. GitHub Repository Secrets

You need to set up these secrets in your GitHub repository settings:

#### PyPI API Token
1. Go to [PyPI Account Settings](https://pypi.org/manage/account/token/)
2. Create a new API token with upload permissions for the `rezen` package
3. Add to GitHub secrets as `PYPI_API_TOKEN`

#### ReZEN API Key (for testing)
1. Add your ReZEN API key as `REZEN_API_KEY` secret
2. This is used for running tests during the release process

### 2. GitHub Environment (Optional but Recommended)

For additional security, create a `release` environment in your repository:

1. Go to Settings → Environments
2. Create environment named `release`
3. Add protection rules:
   - Required reviewers (optional)
   - Deployment branches: only `main` branch
   - Environment secrets can override repository secrets

## 🔄 Automated Workflows

### CI Workflow (`.github/workflows/ci.yml`)

**Triggers:** Every push and pull request to `main` and `develop` branches

**What it does:**
- Tests on Python 3.8-3.12
- Runs linting (flake8, black, isort)
- Type checking (mypy)
- Security checks (safety)
- Code coverage
- Package building and validation

### Release Workflow (`.github/workflows/release.yml`)

**Triggers:** When you push a version tag (e.g., `v1.0.2`)

**What it does:**
1. **Test**: Runs full test suite on all Python versions
2. **Build**: Creates source and wheel distributions
3. **Validate**: Checks version consistency across files
4. **Publish to PyPI**: Uploads package to PyPI
5. **GitHub Release**: Creates GitHub release with:
   - Auto-generated changelog
   - Package files attached
   - Release notes

## 📊 Version Management

### Semantic Versioning

We follow [Semantic Versioning 2.0.0](https://semver.org/):

- **Major** (`1.0.0` → `2.0.0`): Breaking changes
- **Minor** (`1.0.0` → `1.1.0`): New features, backwards compatible
- **Patch** (`1.0.0` → `1.0.1`): Bug fixes, backwards compatible

### Version Bump Script

The `scripts/bump_version.py` script ensures version consistency:

```bash
# Preview changes without making them
python scripts/bump_version.py patch --dry-run

# Bump version only (no git operations)
python scripts/bump_version.py patch

# Bump version and create tag
python scripts/bump_version.py patch --tag

# Bump version, tag, and push (triggers release)
python scripts/bump_version.py patch --push
```

**Files updated:**
- `pyproject.toml` - Main package version
- `rezen/__init__.py` - Python module version

## 🚀 Release Types

### Patch Release (Bug Fixes)

```bash
# Examples: 1.0.0 → 1.0.1, 1.2.5 → 1.2.6
python scripts/bump_version.py patch --push
```

**When to use:**
- Bug fixes
- Documentation updates
- Performance improvements
- Security patches

### Minor Release (New Features)

```bash
# Examples: 1.0.0 → 1.1.0, 1.5.2 → 1.6.0
python scripts/bump_version.py minor --push
```

**When to use:**
- New API endpoints
- New features
- Backwards-compatible changes

### Major Release (Breaking Changes)

```bash
# Examples: 1.5.2 → 2.0.0, 2.3.1 → 3.0.0
python scripts/bump_version.py major --push
```

**When to use:**
- Breaking API changes
- Removed deprecated features
- Major architecture changes

## 📦 Pre-release Versions

For beta/alpha releases, manually create tags with suffixes:

```bash
# Beta release
git tag -a v1.1.0-beta.1 -m "Release v1.1.0-beta.1"
git push --tags

# Alpha release
git tag -a v1.1.0-alpha.1 -m "Release v1.1.0-alpha.1"
git push --tags
```

Pre-release versions will be marked as "pre-release" on GitHub.

## 🔍 Monitoring Releases

### GitHub Actions

Monitor release progress at:
`https://github.com/theperrygroup/rezen/actions`

### PyPI Package

Check published package at:
`https://pypi.org/project/rezen/`

### GitHub Releases

View releases at:
`https://github.com/theperrygroup/rezen/releases`

## ❌ Troubleshooting

### Release Failed to Publish to PyPI

**Common causes:**
- Version already exists on PyPI
- PyPI API token expired/invalid
- Package validation failed

**Solutions:**
1. Check PyPI for existing version
2. Verify `PYPI_API_TOKEN` secret
3. Review workflow logs for specific errors

### Version Mismatch Error

**Error:** "Version mismatch detected!"

**Cause:** Versions in `pyproject.toml` and `rezen/__init__.py` don't match the git tag

**Solution:**
```bash
# Use the bump script to ensure consistency
python scripts/bump_version.py patch --push

# Or manually fix versions and re-tag
```

### GitHub Release Not Created

**Common causes:**
- PyPI publish failed (GitHub release depends on it)
- GitHub token permissions insufficient
- Repository settings blocking release creation

**Solutions:**
1. Check PyPI publish step succeeded
2. Verify repository permissions
3. Review workflow logs

### License Deprecation Warning

**Warning:** `project.license` as a TOML table is deprecated

**Cause:** Newer setuptools versions prefer SPDX license expressions over table format

**Solution:** This is just a warning and won't affect builds. The workflow completes successfully.

**Future fix:** After 2026, update to: `license = "MIT"` once setuptools>=77.0.0 is standard

### Tests Failing During Release

**Cause:** Tests must pass before publishing

**Solution:**
1. Fix failing tests
2. Commit fixes
3. Re-run release process

## 📈 Best Practices

### Pre-Release Checklist

Before creating a release:

- [ ] All tests passing locally
- [ ] Documentation updated
- [ ] CHANGELOG or release notes prepared
- [ ] Version bump type decided (major/minor/patch)
- [ ] Breaking changes documented (if any)

### Post-Release Checklist

After successful release:

- [ ] Verify package on PyPI
- [ ] Test installation: `pip install rezen==<new-version>`
- [ ] Check GitHub release page
- [ ] Update documentation if needed
- [ ] Announce release (if significant)

### Version Strategy

- Use patch releases frequently for small fixes
- Save minor releases for feature sets
- Major releases should be planned and communicated
- Keep backwards compatibility when possible

## 🔐 Security

### API Token Management

- Rotate PyPI tokens periodically
- Use scoped tokens (package-specific, not account-wide)
- Never commit tokens to repository
- Use GitHub environments for additional protection

### Release Process Security

- All releases run through automated testing
- Package integrity verified before publishing
- Source code and distributions included in GitHub releases
- All changes tracked through git history

## 📞 Getting Help

If you encounter issues with the release process:

1. Check workflow logs in GitHub Actions
2. Review this documentation
3. Check PyPI and GitHub status pages
4. Create an issue in the repository

---

## 🎉 Congratulations!

You now have a fully automated release system that will:
✅ Test your code thoroughly
✅ Publish to PyPI automatically  
✅ Create beautiful GitHub releases
✅ Maintain version consistency
✅ Provide detailed release notes

Happy releasing! 🚀 