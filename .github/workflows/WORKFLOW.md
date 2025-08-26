# CI/CD Workflow Documentation

This document explains the enhanced CI/CD pipeline setup for the agents-config repository.

## Workflow Overview

The repository now uses a comprehensive CI/CD pipeline with the following workflows:

1. **CI (ci.yml)** - Runs tests and linting on PRs
2. **Version Bump (version-bump.yml)** - Automatically bumps version and creates tags on PR merge
3. **Release (release.yml)** - Creates GitHub releases when tags are pushed
4. **Publish (publish.yml)** - Publishes to PyPI after successful release

## Workflow Details

### 1. CI Workflow (`ci.yml`)

**Triggers:**
- Pull requests to `master` branch
- Manual dispatch (workflow_dispatch)

**Purpose:**
- Validates code quality before merging
- Runs tests, linting, and type checking
- Provides feedback on PRs

**Jobs:**
- Tests on Python 3.12 and 3.13
- Runs demo script to ensure functionality
- Code quality checks (black, isort, flake8, mypy)
- Coverage reporting to Codecov

### 2. Version Bump Workflow (`version-bump.yml`)

**Triggers:**
- PR merge to `master` branch only

**Purpose:**
- Automatically bumps version based on PR labels
- Updates CHANGELOG.md with release date
- Creates and pushes version tag
- Triggers subsequent release workflow

**Version Bump Logic:**
- Checks PR labels for version bump type:
  - `major` label → Major version bump (1.0.0 → 2.0.0)
  - `minor` label → Minor version bump (1.0.0 → 1.1.0)  
  - `patch` label → Patch version bump (1.0.0 → 1.0.1)
  - No label → Default to patch bump

**Process:**
1. Reads current version from `pyproject.toml`
2. Calculates new version based on bump type
3. Updates `pyproject.toml` and `CHANGELOG.md`
4. Commits changes with `[skip ci]` to avoid triggering CI
5. Creates and pushes version tag (e.g., `v1.2.3`)

### 3. Release Workflow (`release.yml`)

**Triggers:**
- Push of version tags (v*)

**Purpose:**
- Creates GitHub release with release notes
- Triggers publish workflow upon successful completion

**Process:**
1. Creates GitHub release using `softprops/action-gh-release`
2. Generates automatic release notes
3. Includes installation instructions and changelog link
4. Outputs success signal for dependent workflows

### 4. Publish Workflow (`publish.yml`)

**Triggers:**
- Successful completion of release workflow
- Manual dispatch
- Direct tag push (fallback)

**Purpose:**
- Publishes package to PyPI using OIDC trusted publishing
- Ensures only successful releases are published

**Process:**
1. Waits for successful release workflow completion
2. Runs tests and builds package
3. Publishes to PyPI using trusted publishing
4. Provides deployment confirmation

## Development Workflow

### For Feature Development

1. **Create Feature Branch:**
   ```bash
   git checkout -b feat/my-new-feature
   # or
   git checkout -b fix/bug-description
   ```

2. **Develop and Test:**
   - Make your changes
   - Test locally
   - No CI runs automatically on feature branches

3. **Create Pull Request:**
   - Create PR from feature branch to `master`
   - CI workflow automatically runs for validation
   - Add appropriate labels for version bumping:
     - `major` - Breaking changes
     - `minor` - New features (backward compatible)
     - `patch` - Bug fixes (default if no label)

4. **Review and Merge:**
   - Address any CI feedback
   - Get PR reviewed and approved
   - Merge to `master`

### For Release Process

1. **Automatic After PR Merge:**
   - Version bump workflow runs automatically
   - Version is bumped based on PR labels
   - Tag is created and pushed
   - Release workflow is triggered by tag
   - Publish workflow is triggered by successful release

2. **Manual Trigger (if needed):**
   ```bash
   # Manually trigger CI
   gh workflow run ci.yml
   
   # Manually trigger publish (for troubleshooting)
   gh workflow run publish.yml
   ```

## Version Labeling Guide

Add labels to your PRs to control version bumping:

- **🔴 `major`** - For breaking changes (API changes, removed features)
  - Example: Changing import structure, removing public methods
  
- **🟡 `minor`** - For new features (backward compatible)
  - Example: Adding new configuration options, new utility functions
  
- **🟢 `patch`** - For bug fixes and minor improvements (default)
  - Example: Fixing bugs, updating documentation, dependency updates

## Branch Protection

Recommended branch protection rules for `master`:

- Require PR reviews before merging
- Require status checks to pass (CI workflow)
- Require branches to be up to date before merging
- Include administrators in restrictions

## Troubleshooting

### Common Issues

1. **CI not running on feature branch:**
   - This is expected behavior
   - CI only runs on PRs to master or manual dispatch

2. **Version not bumped after PR merge:**
   - Check if PR was properly merged (not force-pushed)
   - Verify version-bump workflow permissions
   - Check workflow logs for errors

3. **Release not published to PyPI:**
   - Verify release workflow completed successfully
   - Check PyPI trusted publishing configuration
   - Review publish workflow logs

### Manual Recovery

If automation fails, you can manually trigger workflows:

```bash
# Create tag manually
git tag v1.2.3
git push origin v1.2.3

# Or use GitHub CLI
gh workflow run release.yml
gh workflow run publish.yml
```

## Monitoring

Monitor workflow execution in:
- GitHub Actions tab in repository
- Email notifications (if configured)
- Status checks on PRs

## Security Considerations

- OIDC trusted publishing eliminates need for PyPI tokens
- Workflows use minimal required permissions
- Sensitive operations only run on protected branches
- Version bumping includes commit verification