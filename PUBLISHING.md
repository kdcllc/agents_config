# PyPI Publishing Guide for agents-config

This guide walks you through the complete process of packaging and publishing the `agents-config` library to PyPI from a GitHub repository using **PyPI Trusted Publishers** (OIDC-based authentication).

## 🚀 Quick Start

1. **Set up PyPI Trusted Publisher for your GitHub repository**
2. **Create a release tag**
3. **GitHub Actions handles the rest automatically!**

## 📋 Prerequisites

### 1. PyPI Account

- Create account at [PyPI.org](https://pypi.org/account/register/)

### 2. PyPI Trusted Publisher Setup

Instead of API tokens, we use PyPI's Trusted Publishers feature for secure, token-less authentication:

#### For New Projects (Recommended)

1. Go to [PyPI Publishing](https://pypi.org/manage/account/publishing/)
2. Click "Add a new pending publisher"
3. Fill in the form:
   - **PyPI project name**: `agents-config`
   - **Owner**: `kdcllc` (your GitHub username)
   - **Repository name**: `agents_config`
   - **Workflow filename**: `publish.yml`
   - **Environment name**: `pypi`
4. Click "Add"

#### For Existing Projects

1. Go to your [PyPI project settings](https://pypi.org/manage/project/agents-config/settings/publishing/)
2. Scroll to "Trusted publishers"
3. Click "Add a trusted publisher"
4. Select "GitHub" and fill in the same details as above

### 3. No GitHub Secrets Required

With Trusted Publishers, you **don't need** to set up any API tokens or GitHub secrets. The OIDC authentication is handled automatically.

## 🔧 Repository Setup

### 1. Update Author Information

Edit `pyproject.toml` and replace placeholder information:

```toml
authors = [
    {name = "Your Real Name", email = "your.real.email@example.com"}
]
```

### 2. Update GitHub URLs

Replace `yourusername` with your actual GitHub username:

```toml
[project.urls]
Homepage = "https://github.com/kdcllc/agents_config"
Repository = "https://github.com/kdcllc/agents_config.git"
"Bug Tracker" = "https://github.com/kdcllc/agents_config/issues"
```

## 📦 Publishing Process

### Option 1: Automatic Release (Recommended)

1. **Update version in pyproject.toml:**

   ```toml
   version = "0.1.1"  # Increment version
   ```

2. **Commit and push changes:**

   ```bash
   git add .
   git commit -m "Bump version to 0.1.1"
   git push origin main
   ```

3. **Create and push a git tag:**

   ```bash
   git tag v0.1.1
   git push origin v0.1.1
   ```

4. **GitHub Actions automatically:**
   - Runs tests across Python 3.12 and 3.13
   - Builds the package
   - Publishes to PyPI
   - Creates a GitHub release

### Option 2: Manual Local Publishing

For emergency releases or local testing:

```bash
# Install build tools
pip install build twine

# Build package
python -m build

# Check package
twine check dist/*

# Upload to PyPI
twine upload dist/*
```

## 🏷️ Version Tagging Strategy

The automated workflow responds to version tags:

- `v1.0.0` → PyPI production release

## 🧪 Testing the Package

After publishing, test installation:

```bash
# Create a fresh virtual environment
python -m venv test-env
source test-env/bin/activate  # Linux/Mac
# or
test-env\Scripts\activate  # Windows

# Install your package
pip install agents-config

# Test import
python -c "from app.agents_config import AIConfig; print('Success!')"
```

## 🔍 Monitoring and Maintenance

### Check Package Status

- [PyPI Project Page](https://pypi.org/project/agents-config/)

### Download Statistics

Monitor usage at:

- [PyPI Stats](https://pypistats.org/packages/agents-config)

### Update Package

1. Make changes to code
2. Update version in `pyproject.toml`
3. Update `CHANGELOG.md` (if you create one)
4. Create new git tag
5. Push tag to trigger release

## 🚨 Troubleshooting

### Common Issues

**1. Package name already exists:**

- Choose a different name in `pyproject.toml`
- Consider: `agents-config-yourname`, `ai-agents-config`, etc.

**2. Authentication fails:**

- Verify PyPI Trusted Publisher is properly configured
- Check that GitHub repository settings match PyPI configuration exactly:
  - Owner: `kdcllc`
  - Repository: `agents_config`
  - Workflow filename: `publish.yml`
  - Environment name: `pypi`
- Ensure the workflow is running on the correct branch/tag
- Verify the `id-token: write` permission is set in the workflow

**3. Build fails:**

- Check `pyproject.toml` syntax
- Verify all dependencies are available
- Test build locally: `python -m build`

**4. Tests fail in CI:**

- Run tests locally first: `uv run pytest`
- Check Python version compatibility
- Verify all dependencies in `pyproject.toml`

### Debugging Commands

```bash
# Test package build locally
python -m build

# Validate package metadata
twine check dist/*

# Check what files are included
tar -tzf dist/agents-config-*.tar.gz

# Test installation from local build
pip install dist/agents-config-*.whl
```

## 📚 Additional Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [PyPI Help](https://pypi.org/help/)
- [GitHub Actions for Python](https://docs.github.com/en/actions/guides/building-and-testing-python)
- [Semantic Versioning](https://semver.org/)

## 🎯 Next Steps

1. **Set up automated testing:** Add more comprehensive tests
2. **Documentation:** Consider using Sphinx for API docs
3. **Code coverage:** Add coverage reporting
4. **Security:** Set up dependency scanning
5. **Changelog:** Maintain a CHANGELOG.md file

## ✅ Checklist

Before first release:

- [ ] Update author information in `pyproject.toml`
- [ ] Update GitHub URLs with your username
- [ ] Create PyPI account
- [ ] Set up PyPI Trusted Publisher for your GitHub repository
- [ ] Test local build: `python -m build`
- [ ] Create first git tag: `git tag v0.1.0`
- [ ] Push tag: `git push origin v0.1.0`
- [ ] Monitor GitHub Actions workflow
- [ ] Verify package on PyPI
- [ ] Test installation: `pip install agents-config`

Your package will be available at: <https://pypi.org/project/agents-config/>
