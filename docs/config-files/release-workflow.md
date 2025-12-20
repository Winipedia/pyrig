# ReleaseWorkflow

## Overview

**File Location:** `.github/workflows/release.yaml`
**ConfigFile Class:** `ReleaseWorkflow`
**File Type:** YAML
**Priority:** Standard

Creates a GitHub Actions workflow that automates the release process. This workflow bumps versions, creates git tags, generates changelogs, and publishes GitHub releases with artifacts.

## Purpose

The `release.yaml` workflow automates releases:

- **Version Bumping** - Automatically increments version numbers
- **Dependency Updates** - Updates and locks dependencies
- **Git Tagging** - Creates version tags
- **Changelog Generation** - Automatically generates release notes
- **GitHub Releases** - Creates releases with artifacts
- **Artifact Management** - Downloads and attaches build artifacts

### Why pyrig manages this file

pyrig creates `release.yaml` to:
1. **Automate releases** - No manual version bumping or tagging
2. **Ensure consistency** - Every release follows the same process
3. **Generate changelogs** - Automatic release notes from commits
4. **Attach artifacts** - Distributable files included in releases
5. **Best practices** - Follows semantic versioning and git flow

The workflow is created during `pyrig init` and runs automatically after the build workflow completes successfully on the main branch.

## File Location

The file is placed in the GitHub workflows directory:

```
my-awesome-project/
├── .github/
│   └── workflows/
│       ├── health_check.yaml
│       ├── build.yaml
│       ├── release.yaml  # <-- Here
│       └── publish.yaml
├── my_awesome_project/
│   └── __init__.py
└── pyproject.toml
```

## Workflow Pipeline

The release workflow is part of the CI/CD pipeline:

```
┌─────────────────┐
│  Health Check   │  Runs on PR/push
│   (CI checks)   │
└────────┬────────┘
         │ ✓ Success on main
         ▼
┌─────────────────┐
│     Build       │  Builds artifacts
│  (OS matrix)    │
└────────┬────────┘
         │ ✓ Success
         ▼
┌─────────────────┐
│    Release      │  ← YOU ARE HERE
│  (Tag + notes)  │
└────────┬────────┘
         │ ✓ Success
         ▼
┌─────────────────┐
│    Publish      │  Publishes to PyPI
│  (PyPI upload)  │
└─────────────────┘
```

## Workflow Triggers

### Automatic Trigger

```yaml
on:
  workflow_run:
    workflows:
      - Build
    types:
      - completed
```

**Triggers when:**
- Build workflow completes
- Only runs if build workflow succeeded
- Only on main branch (configured in build workflow)

### Manual Trigger

```yaml
on:
  workflow_dispatch: {}
```

**Allows:**
- Manual workflow runs from GitHub UI
- Useful for creating releases manually

## Workflow Configuration

### Permissions

```yaml
permissions:
  contents: write
  actions: read
```

**Permissions:**

#### `contents: write`

- **Type:** String
- **Default:** `write`
- **Required:** Yes
- **Purpose:** Allows creating tags and releases
- **Why pyrig sets it:** Workflow needs to push tags and create releases

#### `actions: read`

- **Type:** String
- **Default:** `read`
- **Required:** Yes
- **Purpose:** Allows downloading artifacts from build workflow
- **Why pyrig sets it:** Workflow downloads build artifacts

### Run Name

```yaml
run-name: Release
```

- **Type:** String
- **Default:** `Release`
- **Required:** No
- **Purpose:** Identifies workflow runs in GitHub UI
- **Why pyrig sets it:** Clear identification in workflow list

### Defaults

```yaml
defaults:
  run:
    shell: bash
```

- **Type:** Object
- **Default:** `bash`
- **Required:** No
- **Purpose:** Consistent shell across all steps
- **Why pyrig sets it:** Bash is standard and portable

### Environment Variables

```yaml
env:
  PYTHONDONTWRITEBYTECODE: 1
  UV_NO_SYNC: 1
```

**Variables:**

#### `PYTHONDONTWRITEBYTECODE`

- **Type:** Integer (1 = true)
- **Default:** `1`
- **Required:** No
- **Purpose:** Prevents `.pyc` file creation
- **Why pyrig sets it:** Faster execution, cleaner workspace

#### `UV_NO_SYNC`

- **Type:** Integer (1 = true)
- **Default:** `1`
- **Required:** No
- **Purpose:** Prevents automatic dependency syncing
- **Why pyrig sets it:** Explicit control over when dependencies are installed

## Jobs

### `release` Job

```yaml
jobs:
  release:
    runs-on: ubuntu-latest
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    steps:
      # ... steps here
```

**Configuration:**

#### `runs-on`

- **Type:** String
- **Default:** `ubuntu-latest`
- **Required:** Yes
- **Purpose:** Specifies runner OS
- **Why pyrig sets it:** Linux is standard for Python releases

#### `if` Condition

- **Type:** Expression
- **Default:** `${{ github.event.workflow_run.conclusion == 'success' }}`
- **Required:** No (but recommended)
- **Purpose:** Only runs if build workflow succeeded
- **Why pyrig sets it:** Prevents releases after failed builds

## Steps

### 1. Checkout Repository

```yaml
- name: Checkout Repository
  id: checkout_repository
  uses: actions/checkout@main
  with:
    token: ${{ secrets.REPO_TOKEN }}
```

**Purpose:** Checks out the repository code

**Configuration:**
- **token:** Uses `REPO_TOKEN` for authentication
- **Why REPO_TOKEN:** Allows pushing commits and tags

### 2. Setup Git

```yaml
- name: Setup Git
  id: setup_git
  run: |
    git config --global user.email "github-actions[bot]@users.noreply.github.com"
    git config --global user.name "github-actions[bot]"
```

**Purpose:** Configures git identity

**Why needed:** Required for committing version bumps and creating tags

### 3. Setup Project Management

```yaml
- name: Setup Project Mgt
  id: setup_project_mgt
  uses: astral-sh/setup-uv@main
  with:
    python-version: '3.14'
```

Installs uv and the latest Python version allowed by `requires-python` constraint (currently 3.14)

### 4. Patch Version

```yaml
- name: Patch Version
  id: patch_version
  run: uv version --bump patch && git add pyproject.toml
```

**Purpose:** Bumps the patch version

**What it does:**
- Increments patch version (e.g., 0.1.0 → 0.1.1)
- Updates `pyproject.toml`
- Stages the change for commit

**Why needed:** Each release needs a new version number

### 5. Install Python Dependencies

```yaml
- name: Install Python Dependencies
  id: install_python_dependencies
  run: uv lock --upgrade && uv sync
```

**Purpose:** Updates and installs dependencies

**What it does:**
- Updates `uv.lock` with latest compatible versions
- Installs all dependencies
- Ensures lock file is current

**Why needed:** Dependencies should be up-to-date for releases

### 6. Add Dependency Updates To Git

```yaml
- name: Add Dependency Updates To Git
  id: add_dependency_updates_to_git
  run: git add pyproject.toml uv.lock
```

**Purpose:** Stages dependency changes

**What it does:**
- Stages `pyproject.toml` (version bump)
- Stages `uv.lock` (dependency updates)

**Why needed:** Changes need to be committed

### 7. Run Pre Commit Hooks

```yaml
- name: Run Pre Commit Hooks
  id: run_pre_commit_hooks
  run: uv run pre-commit run --all-files
```

**Purpose:** Runs code quality checks

**What it does:**
- Runs ruff formatting
- Runs ruff linting
- Runs mypy type checking
- Runs other configured hooks

**Why needed:** Ensures code quality before release

### 8. Commit Added Changes

```yaml
- name: Commit Added Changes
  id: commit_added_changes
  run: |
    git commit --no-verify -m '[skip ci] CI/CD: Committing possible added changes (e.g.: pyproject.toml)'
```

**Purpose:** Commits version bump and dependency updates

**What it does:**
- Commits staged changes
- Uses `--no-verify` to skip pre-commit hooks (already ran)
- Uses `[skip ci]` to prevent triggering workflows

**Why needed:** Changes must be committed before tagging

### 9. Push Commits

```yaml
- name: Push Commits
  id: push_commits
  run: git push
```

**Purpose:** Pushes commits to remote

**What it does:**
- Pushes version bump commit to main branch

**Why needed:** Commits must be on remote before tagging

### 10. Create And Push Tag

```yaml
- name: Create And Push Tag
  id: create_and_push_tag
  run: git tag v$(uv version --short) && git push origin v$(uv version --short)
```

**Purpose:** Creates and pushes version tag

**What it does:**
- Creates tag like `v0.1.1`
- Pushes tag to remote

**Why needed:** Tags mark release points in git history

### 11. Extract Version

```yaml
- name: Extract Version
  id: extract_version
  run: echo "version=v$(uv version --short)" >> $GITHUB_OUTPUT
```

**Purpose:** Exports version for later steps

**What it does:**
- Outputs version to `$GITHUB_OUTPUT`
- Makes version available to subsequent steps

**Why needed:** Release creation step needs the version

### 12. Download Artifacts From Workflow Run

```yaml
- name: Download Artifacts From Workflow Run
  id: download_artifacts_from_workflow_run
  uses: actions/download-artifact@main
  with:
    path: dist
    run-id: ${{ github.event.workflow_run.id }}
    github-token: ${{ secrets.GITHUB_TOKEN }}
    merge-multiple: 'true'
```

**Purpose:** Downloads build artifacts

**Configuration:**
- **path:** `dist` directory
- **run-id:** Build workflow run ID
- **merge-multiple:** Merges artifacts from matrix builds

**What it does:**
- Downloads wheels from build workflow
- Places them in `dist/` directory

**Why needed:** Artifacts are attached to GitHub release

### 13. Build Changelog

```yaml
- name: Build Changelog
  id: build_changelog
  uses: mikepenz/release-changelog-builder-action@develop
  with:
    token: ${{ secrets.GITHUB_TOKEN }}
```

**Purpose:** Generates changelog from commits

**What it does:**
- Analyzes commits since last release
- Groups commits by type (features, fixes, etc.)
- Generates formatted changelog

**Why needed:** Release notes document what changed

### 14. Create Release

```yaml
- name: Create Release
  id: create_release
  uses: ncipollo/release-action@main
  with:
    tag: ${{ steps.extract_version.outputs.version }}
    name: ${{ github.event.repository.name }} ${{ steps.extract_version.outputs.version }}
    body: ${{ steps.build_changelog.outputs.changelog }}
    artifacts: dist/*
```

**Purpose:** Creates GitHub release

**Configuration:**
- **tag:** Version tag (e.g., `v0.1.1`)
- **name:** Release name (e.g., `my-awesome-project v0.1.1`)
- **body:** Changelog content
- **artifacts:** All files in `dist/`

**What it does:**
- Creates GitHub release
- Attaches changelog
- Attaches build artifacts

**Why needed:** This is the main purpose of the workflow

## Default Configuration

For a project named `my-awesome-project`:

**File location:** `.github/workflows/release.yaml`

**File contents:**
```yaml
name: Release
'on':
  workflow_dispatch: {}
  workflow_run:
    workflows:
    - Build
    types:
    - completed
permissions:
  contents: write
  actions: read
run-name: Release
defaults:
  run:
    shell: bash
env:
  PYTHONDONTWRITEBYTECODE: 1
  UV_NO_SYNC: 1
jobs:
  release:
    runs-on: ubuntu-latest
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    steps:
    - name: Checkout Repository
      id: checkout_repository
      uses: actions/checkout@main
      with:
        token: ${{ secrets.REPO_TOKEN }}
    - name: Setup Git
      id: setup_git
      run: git config --global user.email "github-actions[bot]@users.noreply.github.com"
        && git config --global user.name "github-actions[bot]"
    - name: Setup Project Mgt
      id: setup_project_mgt
      uses: astral-sh/setup-uv@main
      with:
        python-version: '3.14'
    - name: Patch Version
      id: patch_version
      run: uv version --bump patch && git add pyproject.toml
    - name: Install Python Dependencies
      id: install_python_dependencies
      run: uv lock --upgrade && uv sync
    - name: Add Dependency Updates To Git
      id: add_dependency_updates_to_git
      run: git add pyproject.toml uv.lock
    - name: Run Pre Commit Hooks
      id: run_pre_commit_hooks
      run: uv run pre-commit run --all-files
    - name: Commit Added Changes
      id: commit_added_changes
      run: 'git commit --no-verify -m ''[skip ci] CI/CD: Committing possible added
        changes (e.g.: pyproject.toml)'''
    - name: Push Commits
      id: push_commits
      run: git push
    - name: Create And Push Tag
      id: create_and_push_tag
      run: git tag v$(uv version --short) && git push origin v$(uv version --short)
    - name: Extract Version
      id: extract_version
      run: echo "version=v$(uv version --short)" >> $GITHUB_OUTPUT
    - name: Download Artifacts From Workflow Run
      id: download_artifacts_from_workflow_run
      uses: actions/download-artifact@main
      with:
        path: dist
        run-id: ${{ github.event.workflow_run.id }}
        github-token: ${{ secrets.GITHUB_TOKEN }}
        merge-multiple: 'true'
    - name: Build Changelog
      id: build_changelog
      uses: mikepenz/release-changelog-builder-action@develop
      with:
        token: ${{ secrets.GITHUB_TOKEN }}
    - name: Create Release
      id: create_release
      uses: ncipollo/release-action@main
      with:
        tag: ${{ steps.extract_version.outputs.version }}
        name: ${{ github.event.repository.name }} ${{ steps.extract_version.outputs.version
          }}
        body: ${{ steps.build_changelog.outputs.changelog }}
        artifacts: dist/*
```

## Required Secrets

### `REPO_TOKEN`

The workflow requires a GitHub Personal Access Token:

**Setup:**

1. **Create Personal Access Token:**
   - Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Click "Generate new token (classic)"
   - Name: `GitHub Actions`
   - Expiration: Choose appropriate expiration
   - Scopes:
     - Select `contents` → `read` and `write` (required for pushing commits and tags)
     - Select `administration` → `read` and `write` (required for repo and branch protection settings)
     - Select `pages` → `read` and `write` (required for GitHub Pages deployment)
   - Click "Generate token"
   - Copy the token (starts with `ghp_`)

2. **Add to GitHub secrets:**
   - Go to repository Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `REPO_TOKEN`
   - Value: Paste the GitHub token
   - Click "Add secret"

**Why needed:**
- Default `GITHUB_TOKEN` can't trigger workflows
- `REPO_TOKEN` allows pushing commits and tags
- Enables workflow chaining (release → publish)
- Pages scope required for deploying documentation to GitHub Pages

**Security:**
- Token is encrypted in GitHub
- Only accessible to workflows
- Never exposed in logs
- Can be revoked anytime

## Workflow Execution

### Automatic Execution

When the build workflow completes successfully on main:

1. **Build workflow finishes** - Artifacts uploaded
2. **Release workflow triggers** - Automatically starts
3. **Checks condition** - Verifies build succeeded
4. **Bumps version** - Increments patch version
5. **Updates dependencies** - Locks latest versions
6. **Runs quality checks** - Pre-commit hooks
7. **Commits changes** - Version bump and lock file
8. **Pushes commits** - To main branch
9. **Creates tag** - Version tag (e.g., `v0.1.1`)
10. **Downloads artifacts** - From build workflow
11. **Generates changelog** - From commit messages
12. **Creates release** - GitHub release with artifacts

### Manual Execution

To manually trigger the workflow:

1. **Go to Actions tab** in GitHub
2. **Select "Release" workflow**
3. **Click "Run workflow"**
4. **Select branch** (usually `main`)
5. **Click "Run workflow"** button

**When to use:**
- Create release without waiting for build
- Retry failed release
- Create release from specific commit

## Version Bumping

### Automatic Patch Bumps

By default, the workflow bumps the patch version:

```
0.1.0 → 0.1.1 → 0.1.2 → ...
```

### Custom Version Bumps

To bump minor or major versions:

```python
# my_awesome_project/dev/configs/workflows/release.py
from pyrig.dev.configs.workflows.release import ReleaseWorkflow
from typing import Any


class CustomReleaseWorkflow(ReleaseWorkflow):
    """Custom release workflow with minor version bumps."""

    @classmethod
    def step_patch_version(cls, *, step: dict[str, Any] | None = None) -> dict[str, Any]:
        """Bump minor version instead of patch."""
        return cls.get_step(
            step_func=cls.step_patch_version,
            run="uv version --bump minor && git add pyproject.toml",
            step=step,
        )
```

### Manual Version Setting

To set a specific version:

```bash
# Locally
uv version 1.0.0
git add pyproject.toml
git commit -m "Bump to 1.0.0"
git push

# Then trigger release workflow manually
```

## Changelog Generation

### Automatic Changelog

The workflow uses [release-changelog-builder-action](https://github.com/mikepenz/release-changelog-builder-action) to generate changelogs from commit messages.

**Example changelog:**

```markdown
## What's Changed
### 🚀 Features
* Add new feature by @username in #123
* Improve performance by @username in #124

### 🐛 Bug Fixes
* Fix critical bug by @username in #125

### 📝 Documentation
* Update README by @username in #126

**Full Changelog**: https://github.com/username/my-awesome-project/compare/v0.1.0...v0.1.1
```

### Commit Message Conventions

For better changelogs, use conventional commits:

```bash
# Features
git commit -m "feat: add new feature"
git commit -m "feature: add new feature"

# Bug fixes
git commit -m "fix: resolve critical bug"
git commit -m "bugfix: resolve critical bug"

# Documentation
git commit -m "docs: update README"

# Chores
git commit -m "chore: update dependencies"
```

## Monitoring

### Viewing Workflow Runs

```bash
# In GitHub UI
Repository → Actions → Release

# View specific run
Click on run → View jobs → View steps
```

### Checking Releases

```bash
# In GitHub UI
Repository → Releases

# View specific release
Click on release → View assets and changelog
```

### Logs

Each step produces logs showing:

```
Checkout Repository ✓
Setup Git ✓
Setup Project Mgt ✓
Patch Version ✓
  Bumped version from 0.1.0 to 0.1.1
Install Python Dependencies ✓
  Updated 5 dependencies
Add Dependency Updates To Git ✓
Run Pre Commit Hooks ✓
  ruff...Passed
  mypy...Passed
Commit Added Changes ✓
Push Commits ✓
Create And Push Tag ✓
  Created tag v0.1.1
Extract Version ✓
Download Artifacts From Workflow Run ✓
  Downloaded 3 artifacts
Build Changelog ✓
Create Release ✓
  Created release: https://github.com/username/my-awesome-project/releases/tag/v0.1.1
```

## Customization

### Custom Version Bump Strategy

```python
# my_awesome_project/dev/configs/workflows/release.py
from pyrig.dev.configs.workflows.release import ReleaseWorkflow
from typing import Any


class CustomReleaseWorkflow(ReleaseWorkflow):
    """Custom release workflow with conditional version bumps."""

    @classmethod
    def step_patch_version(cls, *, step: dict[str, Any] | None = None) -> dict[str, Any]:
        """Bump version based on commit messages."""
        return cls.get_step(
            step_func=cls.step_patch_version,
            run="""
            if git log --format=%B -n 1 | grep -q "BREAKING CHANGE"; then
              uv version --bump major
            elif git log --format=%B -n 1 | grep -q "feat:"; then
              uv version --bump minor
            else
              uv version --bump patch
            fi
            git add pyproject.toml
            """,
            step=step,
        )
```

### Additional Release Steps

```python
# my_awesome_project/dev/configs/workflows/release.py
from pyrig.dev.configs.workflows.release import ReleaseWorkflow
from typing import Any


class CustomReleaseWorkflow(ReleaseWorkflow):
    """Custom release workflow with notifications."""

    @classmethod
    def steps_release(cls) -> list[dict[str, Any]]:
        """Add notification step."""
        return [
            *super().steps_release(),
            cls.step_notify_slack(),
        ]

    @classmethod
    def step_notify_slack(cls, *, step: dict[str, Any] | None = None) -> dict[str, Any]:
        """Notify Slack after release."""
        return cls.get_step(
            step_func=cls.step_notify_slack,
            run='curl -X POST -H "Content-type: application/json" --data \'{"text":"Released ${{ steps.extract_version.outputs.version }}!"}\' ${{ secrets.SLACK_WEBHOOK }}',
            step=step,
        )
```

## Related Files

- **`.github/workflows/build.yaml`** - Builds artifacts ([build-workflow.md](build-workflow.md))
- **`.github/workflows/publish.yaml`** - Publishes to PyPI ([publish-workflow.md](publish-workflow.md))
- **`.github/workflows/health_check.yaml`** - Runs tests ([health-check-workflow.md](health-check-workflow.md))
- **`pyproject.toml`** - Project configuration ([pyproject.md](pyproject.md))
- **`uv.lock`** - Dependency lock file

## Common Issues

### Issue: REPO_TOKEN not found

**Symptom:** Workflow fails with "REPO_TOKEN not found"

**Cause:** Secret not configured in GitHub

**Solution:**

```bash
# Add REPO_TOKEN secret
1. Create Personal Access Token (see Required Secrets section)
2. Go to repository Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: REPO_TOKEN
5. Value: Your GitHub token (starts with ghp_)
6. Click "Add secret"
```

### Issue: Push rejected

**Symptom:** "Push Commits" step fails with "rejected"

**Cause:** Branch protection rules prevent direct pushes

**Solution:**

```bash
# Option 1: Allow GitHub Actions to bypass branch protection
Repository Settings → Branches → Branch protection rules → Edit
Check "Allow specified actors to bypass required pull requests"
Add "github-actions[bot]"

# Option 2: Use a different branch for releases
# Customize workflow to create release branch instead of pushing to main
```

### Issue: Workflow doesn't trigger

**Symptom:** Release workflow doesn't run after build

**Cause:** Build workflow failed or not on main branch

**Solution:**

```bash
# Check build workflow status
Repository → Actions → Build → View latest run

# Ensure build ran on main branch
# If build succeeded, check release workflow condition

# Manual trigger if needed
Repository → Actions → Release → Run workflow
```

### Issue: Changelog is empty

**Symptom:** Release has no changelog content

**Cause:** No commits since last release

**Solution:**

This is normal if there are no new commits. The changelog will be empty.

### Issue: Artifacts not found

**Symptom:** "Download Artifacts" step fails

**Cause:** Build workflow didn't upload artifacts

**Solution:**

```bash
# Check build workflow
Repository → Actions → Build → View latest run
# Verify "Upload Artifacts" step succeeded

# If build didn't run, trigger it manually
Repository → Actions → Build → Run workflow
```

### Issue: Pre-commit hooks fail

**Symptom:** "Run Pre Commit Hooks" step fails

**Cause:** Code doesn't pass quality checks

**Solution:**

```bash
# Run pre-commit locally
uv run pre-commit run --all-files

# Fix any issues
# Commit and push fixes
# Workflow will run again
```

### Issue: Want to skip dependency updates

**Symptom:** Don't want to update dependencies on every release

**Cause:** Default workflow updates dependencies

**Solution:**

```python
# my_awesome_project/dev/configs/workflows/release.py
from pyrig.dev.configs.workflows.release import ReleaseWorkflow
from typing import Any


class CustomReleaseWorkflow(ReleaseWorkflow):
    """Release workflow without dependency updates."""

    @classmethod
    def step_install_python_dependencies(cls, *, step: dict[str, Any] | None = None, no_dev: bool = False) -> dict[str, Any]:
        """Install dependencies without upgrading."""
        return cls.get_step(
            step_func=cls.step_install_python_dependencies,
            run="uv sync",  # Remove --upgrade flag
            step=step,
        )
```

## Best Practices

### ✅ DO

- **Use conventional commits** - Better changelogs
- **Review releases** - Check release notes before publishing
- **Monitor workflow runs** - Watch for failures
- **Test locally first** - Run pre-commit before pushing
- **Use semantic versioning** - Follow semver principles

### ❌ DON'T

- **Don't skip version bumps** - Every release needs a new version
- **Don't ignore failures** - Investigate and fix issues
- **Don't manually create tags** - Let the workflow handle it
- **Don't bypass quality checks** - Pre-commit hooks are important
- **Don't commit directly to main** - Use pull requests

## Advanced Usage

### Conditional Releases

```python
# my_awesome_project/dev/configs/workflows/release.py
from pyrig.dev.configs.workflows.release import ReleaseWorkflow
from typing import Any


class CustomReleaseWorkflow(ReleaseWorkflow):
    """Only release on specific conditions."""

    @classmethod
    def job_release(cls) -> dict[str, Any]:
        """Add custom condition."""
        job = super().job_release()
        job["release"]["if"] = "${{ github.ref == 'refs/heads/main' && !contains(github.event.head_commit.message, '[skip release]') && github.event.workflow_run.conclusion == 'success' }}"
        return job
```

### Pre-release Versions

```python
# my_awesome_project/dev/configs/workflows/release.py
from pyrig.dev.configs.workflows.release import ReleaseWorkflow
from typing import Any


class CustomReleaseWorkflow(ReleaseWorkflow):
    """Create pre-release versions."""

    @classmethod
    def step_create_release(cls, *, step: dict[str, Any] | None = None, artifacts_pattern: str = "dist/*") -> dict[str, Any]:
        """Mark as pre-release."""
        release_step = super().step_create_release(step=step, artifacts_pattern=artifacts_pattern)
        release_step["with"]["prerelease"] = "true"
        return release_step
```

## See Also

- [Semantic Versioning](https://semver.org/) - Version numbering standard
- [Conventional Commits](https://www.conventionalcommits.org/) - Commit message convention
- [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github) - GitHub release documentation
- [Build Workflow](build-workflow.md) - Builds artifacts
- [Publish Workflow](publish-workflow.md) - Publishes to PyPI
- [Getting Started Guide](../getting-started.md) - Initial project setup


