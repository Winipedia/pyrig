# PublishWorkflow

## Overview

**File Location:** `.github/workflows/publish.yaml`
**ConfigFile Class:** `PublishWorkflow`
**File Type:** YAML
**Priority:** Standard

Creates a GitHub Actions workflow that publishes your package to PyPI after a successful release. This workflow builds the wheel and uploads it to PyPI automatically.

## Purpose

The `publish.yaml` workflow automates PyPI publishing:

- **Automatic Publishing** - Publishes to PyPI after successful releases
- **Build Wheel** - Creates distribution package
- **Secure Publishing** - Uses PyPI tokens for authentication
- **Workflow Chaining** - Triggers after release workflow completes
- **Manual Override** - Can be triggered manually if needed

### Why pyrig manages this file

pyrig creates `publish.yaml` to:
1. **Automate publishing** - No manual PyPI uploads
2. **Ensure quality** - Only publishes after all checks pass
3. **Prevent errors** - Consistent, tested publishing process
4. **Save time** - Automatic deployment on release
5. **Best practices** - Follows GitHub Actions and PyPI standards

The workflow is created during `pyrig init` and runs automatically after the release workflow completes successfully.

## File Location

The file is placed in the GitHub workflows directory:

```
my-awesome-project/
├── .github/
│   └── workflows/
│       ├── health_check.yaml
│       ├── build.yaml
│       ├── release.yaml
│       └── publish.yaml  # <-- Here
├── my_awesome_project/
│   └── __init__.py
└── pyproject.toml
```

## Workflow Pipeline

The publish workflow is part of the CI/CD pipeline:

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
│    Release      │  Creates GitHub release
│  (Tag + notes)  │
└────────┬────────┘
         │ ✓ Success
         ▼
┌─────────────────┐
│    Publish      │  ← YOU ARE HERE
│  (PyPI upload)  │
└─────────────────┘
```

## Workflow Triggers

### Automatic Trigger

```yaml
on:
  workflow_run:
    workflows:
      - Release
    types:
      - completed
```

**Triggers when:**
- Release workflow completes
- Only runs if release workflow succeeded

### Manual Trigger

```yaml
on:
  workflow_dispatch: {}
```

**Allows:**
- Manual workflow runs from GitHub UI
- Useful for republishing or fixing issues

## Workflow Configuration

### Permissions

```yaml
permissions: {}
```

- **Type:** Empty permissions
- **Default:** No special permissions needed
- **Required:** No
- **Purpose:** Minimal permissions for security
- **Why pyrig sets it:** Publishing uses PyPI token, not GitHub permissions

### Run Name

```yaml
run-name: Publish
```

- **Type:** String
- **Default:** `Publish`
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

### `publish` Job

```yaml
jobs:
  publish:
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
- **Why pyrig sets it:** Linux is standard for Python publishing

#### `if` Condition

- **Type:** Expression
- **Default:** `${{ github.event.workflow_run.conclusion == 'success' }}`
- **Required:** No (but recommended)
- **Purpose:** Only runs if release workflow succeeded
- **Why pyrig sets it:** Prevents publishing after failed releases

## Steps

### 1. Checkout Repository

```yaml
- name: Checkout Repository
  id: checkout_repository
  uses: actions/checkout@main
```

**Purpose:** Checks out the repository code

**Why needed:** Access to `pyproject.toml` and source code

### 2. Setup Git

```yaml
- name: Setup Git
  id: setup_git
  run: |
    git config --global user.email "github-actions[bot]@users.noreply.github.com"
    git config --global user.name "github-actions[bot]"
```

**Purpose:** Configures git identity

**Why needed:** Required for any git operations (though not used in publish)

### 3. Setup Project Management

```yaml
- name: Setup Project Mgt
  id: setup_project_mgt
  uses: astral-sh/setup-uv@main
  with:
    python-version: '3.14'
```

**Purpose:** Installs uv and Python

**Configuration:**
- **Python version:** Latest supported version (3.14)
- **uv:** Latest version from astral-sh/setup-uv

**Why needed:** uv is used for building and publishing

### 4. Build Wheel

```yaml
- name: Build Wheel
  id: build_wheel
  run: uv build
```

**Purpose:** Builds the Python wheel distribution

**What it does:**
- Creates `dist/` directory
- Builds wheel (`.whl`) file
- Builds source distribution (`.tar.gz`) file

**Why needed:** PyPI requires distribution files

### 5. Publish To PyPI

```yaml
- name: Publish To Pypi
  id: publish_to_pypi
  run: uv publish --token ${{ secrets.PYPI_TOKEN }}
```

**Purpose:** Uploads package to PyPI

**What it does:**
- Authenticates with PyPI using token
- Uploads wheel and source distribution
- Makes package available on PyPI

**Why needed:** This is the main purpose of the workflow

## Default Configuration

For a project named `my-awesome-project`:

**File location:** `.github/workflows/publish.yaml`

**File contents:**
```yaml
name: Publish
'on':
  workflow_dispatch: {}
  workflow_run:
    workflows:
    - Release
    types:
    - completed
permissions: {}
run-name: Publish
defaults:
  run:
    shell: bash
env:
  PYTHONDONTWRITEBYTECODE: 1
  UV_NO_SYNC: 1
jobs:
  publish:
    runs-on: ubuntu-latest
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    steps:
    - name: Checkout Repository
      id: checkout_repository
      uses: actions/checkout@main
    - name: Setup Git
      id: setup_git
      run: git config --global user.email "github-actions[bot]@users.noreply.github.com"
        && git config --global user.name "github-actions[bot]"
    - name: Setup Project Mgt
      id: setup_project_mgt
      uses: astral-sh/setup-uv@main
      with:
        python-version: '3.14'
    - name: Build Wheel
      id: build_wheel
      run: uv build
    - name: Publish To Pypi
      id: publish_to_pypi
      run: uv publish --token ${{ secrets.PYPI_TOKEN }}
```

## Required Secrets

### `PYPI_TOKEN`

The workflow requires a PyPI API token:

**Setup:**

1. **Create PyPI account** at [pypi.org](https://pypi.org)
2. **Generate API token:**
   - Go to Account Settings → API tokens
   - Click "Add API token"
   - Name: `GitHub Actions`
   - Scope: Entire account (or specific project)
   - Copy the token (starts with `pypi-`)
3. **Add to GitHub secrets:**
   - Go to repository Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `PYPI_TOKEN`
   - Value: Paste the PyPI token
   - Click "Add secret"

**Security:**
- Token is encrypted in GitHub
- Only accessible to workflows
- Never exposed in logs
- Can be revoked anytime

## Workflow Execution

### Automatic Execution

When the release workflow completes successfully:

1. **Release workflow finishes** - Creates GitHub release
2. **Publish workflow triggers** - Automatically starts
3. **Checks condition** - Verifies release succeeded
4. **Builds wheel** - Creates distribution files
5. **Publishes to PyPI** - Uploads package
6. **Package available** - Users can `pip install my-awesome-project`

### Manual Execution

To manually trigger the workflow:

1. **Go to Actions tab** in GitHub
2. **Select "Publish" workflow**
3. **Click "Run workflow"**
4. **Select branch** (usually `main`)
5. **Click "Run workflow"** button

**When to use:**
- Republish after PyPI issues
- Publish without creating a new release
- Test publishing process

## Monitoring

### Viewing Workflow Runs

```bash
# In GitHub UI
Repository → Actions → Publish

# View specific run
Click on run → View jobs → View steps
```

### Checking PyPI

```bash
# Check if package is published
pip index versions my-awesome-project

# Or visit PyPI
https://pypi.org/project/my-awesome-project/
```

### Logs

Each step produces logs:

```
Checkout Repository ✓
Setup Git ✓
Setup Project Mgt ✓
Build Wheel ✓
  Building my-awesome-project
  Built dist/my_awesome_project-0.1.0-py3-none-any.whl
  Built dist/my_awesome_project-0.1.0.tar.gz
Publish To Pypi ✓
  Uploading my_awesome_project-0.1.0-py3-none-any.whl
  Uploading my_awesome_project-0.1.0.tar.gz
  View at: https://pypi.org/project/my-awesome-project/0.1.0/
```

## Customization

You can customize the workflow by subclassing:

```python
# my_awesome_project/dev/configs/workflows/publish.py
from pyrig.dev.configs.workflows.publish import PublishWorkflow
from typing import Any


class CustomPublishWorkflow(PublishWorkflow):
    """Custom publish workflow with additional steps."""

    @classmethod
    def steps_publish(cls) -> list[dict[str, Any]]:
        """Add custom steps to publishing."""
        return [
            *super().steps_publish(),
            cls.step_notify_slack(),  # Custom step
        ]

    @classmethod
    def step_notify_slack(cls, *, step: dict[str, Any] | None = None) -> dict[str, Any]:
        """Notify Slack after publishing."""
        return cls.get_step(
            step_func=cls.step_notify_slack,
            run='curl -X POST -H "Content-type: application/json" --data \'{"text":"Published to PyPI!"}\' ${{ secrets.SLACK_WEBHOOK }}',
            step=step,
        )
```

## Related Files

- **`.github/workflows/release.yaml`** - Creates releases ([release-workflow.md](release-workflow.md))
- **`.github/workflows/build.yaml`** - Builds artifacts ([build-workflow.md](build-workflow.md))
- **`.github/workflows/health_check.yaml`** - Runs tests ([health-check-workflow.md](health-check-workflow.md))
- **`pyproject.toml`** - Project configuration ([pyproject.md](pyproject.md))

## Common Issues

### Issue: PYPI_TOKEN not found

**Symptom:** Workflow fails with "PYPI_TOKEN not found"

**Cause:** Secret not configured in GitHub

**Solution:**

```bash
# Add PYPI_TOKEN secret
1. Go to repository Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: PYPI_TOKEN
4. Value: Your PyPI token (starts with pypi-)
5. Click "Add secret"
```

### Issue: Package already exists on PyPI

**Symptom:** Workflow fails with "File already exists"

**Cause:** Version already published to PyPI

**Solution:**

PyPI doesn't allow overwriting versions. You must:

```bash
# Bump version in pyproject.toml
uv version --bump patch  # or minor, or major

# Commit and push
git add pyproject.toml
git commit -m "Bump version"
git push

# Trigger new release
# The publish workflow will run with new version
```

### Issue: Workflow doesn't trigger

**Symptom:** Publish workflow doesn't run after release

**Cause:** Release workflow failed or condition not met

**Solution:**

```bash
# Check release workflow status
Repository → Actions → Release → View latest run

# If release failed, fix the issue and re-run
# If release succeeded, check publish workflow condition

# Manual trigger if needed
Repository → Actions → Publish → Run workflow
```

### Issue: Build fails

**Symptom:** "Build Wheel" step fails

**Cause:** Invalid `pyproject.toml` or missing files

**Solution:**

```bash
# Test build locally
uv build

# Check for errors
# Fix pyproject.toml or missing files
# Commit and push fixes
```

### Issue: Publish fails with authentication error

**Symptom:** "Invalid or expired token"

**Cause:** PyPI token is invalid or expired

**Solution:**

```bash
# Generate new PyPI token
1. Go to pypi.org → Account Settings → API tokens
2. Revoke old token
3. Create new token
4. Update PYPI_TOKEN secret in GitHub
```

### Issue: Want to publish to TestPyPI first

**Symptom:** Want to test publishing before going to production PyPI

**Cause:** Default workflow publishes to production PyPI

**Solution:**

```python
# my_awesome_project/dev/configs/workflows/publish.py
from pyrig.dev.configs.workflows.publish import PublishWorkflow
from typing import Any


class CustomPublishWorkflow(PublishWorkflow):
    """Publish to TestPyPI."""

    @classmethod
    def step_publish_to_pypi(cls, *, step: dict[str, Any] | None = None) -> dict[str, Any]:
        """Publish to TestPyPI instead."""
        return cls.get_step(
            step_func=cls.step_publish_to_pypi,
            run=f"uv publish --token {cls.insert_secret('TEST_PYPI_TOKEN')} --publish-url https://test.pypi.org/legacy/",
            step=step,
        )
```

Then add `TEST_PYPI_TOKEN` secret with token from [test.pypi.org](https://test.pypi.org).

## Best Practices

### ✅ DO

- **Use API tokens** - More secure than username/password
- **Scope tokens** - Limit to specific projects when possible
- **Monitor workflow runs** - Check for failures
- **Test locally first** - Run `uv build` before pushing
- **Verify on PyPI** - Check package after publishing

### ❌ DON'T

- **Don't commit tokens** - Always use GitHub secrets
- **Don't skip version bumps** - PyPI won't accept duplicate versions
- **Don't publish manually** - Let the workflow handle it
- **Don't ignore failures** - Investigate and fix issues
- **Don't use weak tokens** - Use project-scoped tokens

## Advanced Usage

### Conditional Publishing

```python
# my_awesome_project/dev/configs/workflows/publish.py
from pyrig.dev.configs.workflows.publish import PublishWorkflow
from typing import Any


class CustomPublishWorkflow(PublishWorkflow):
    """Only publish on main branch."""

    @classmethod
    def job_publish(cls) -> dict[str, Any]:
        """Add branch condition."""
        job = super().job_publish()
        job["publish"]["if"] = "${{ github.ref == 'refs/heads/main' && github.event.workflow_run.conclusion == 'success' }}"
        return job
```

### Multiple Package Indexes

```python
# my_awesome_project/dev/configs/workflows/publish.py
from pyrig.dev.configs.workflows.publish import PublishWorkflow
from typing import Any


class CustomPublishWorkflow(PublishWorkflow):
    """Publish to multiple indexes."""

    @classmethod
    def steps_publish(cls) -> list[dict[str, Any]]:
        """Publish to PyPI and private index."""
        return [
            *cls.steps_core_setup(),
            cls.step_build_wheel(),
            cls.step_publish_to_pypi(),
            cls.step_publish_to_private_index(),
        ]

    @classmethod
    def step_publish_to_private_index(cls, *, step: dict[str, Any] | None = None) -> dict[str, Any]:
        """Publish to private package index."""
        return cls.get_step(
            step_func=cls.step_publish_to_private_index,
            run=f"uv publish --token {cls.insert_secret('PRIVATE_INDEX_TOKEN')} --publish-url https://private.example.com/simple/",
            step=step,
        )
```

## See Also

- [PyPI Documentation](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/) - Publishing with GitHub Actions
- [uv Documentation](https://docs.astral.sh/uv/) - uv package manager
- [GitHub Actions Documentation](https://docs.github.com/en/actions) - Workflow syntax
- [Release Workflow](release-workflow.md) - Creates GitHub releases
- [Build Workflow](build-workflow.md) - Builds artifacts
- [Getting Started Guide](../getting-started.md) - Initial project setup


