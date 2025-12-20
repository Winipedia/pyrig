# PublishWorkflow

## Overview

**File Location:** `.github/workflows/publish.yaml`
**ConfigFile Class:** `PublishWorkflow`
**File Type:** YAML
**Priority:** Standard

Creates a GitHub Actions workflow that publishes your package to PyPI and documentation to GitHub Pages after a successful release. This workflow builds the wheel, uploads it to PyPI, builds the documentation, and deploys it to GitHub Pages automatically.

## Purpose

The `publish.yaml` workflow automates PyPI publishing and documentation deployment:

- **Automatic Publishing** - Publishes to PyPI after successful releases
- **Documentation Deployment** - Builds and deploys documentation to GitHub Pages
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
│ (PyPI + Docs)   │
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

Triggers when Release workflow completes successfully

### Manual Trigger

```yaml
on:
  workflow_dispatch: {}
```

Allows manual workflow runs from GitHub UI

## Workflow Configuration

### Permissions

```yaml
permissions:
  contents: write
```

Requires `contents: write` permission to push documentation to the `gh-pages` branch

### Run Name

```yaml
run-name: Publish
```

### Defaults

```yaml
defaults:
  run:
    shell: bash
```

### Environment Variables

```yaml
env:
  PYTHONDONTWRITEBYTECODE: 1
  UV_NO_SYNC: 1
```

- `PYTHONDONTWRITEBYTECODE: 1` - Prevents `.pyc` file creation
- `UV_NO_SYNC: 1` - Prevents automatic dependency syncing

## Jobs

The workflow contains two parallel jobs:

### `publish_package` Job

```yaml
jobs:
  publish_package:
    runs-on: ubuntu-latest
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    steps:
      # ... steps here
```

Runs on `ubuntu-latest` only if release workflow succeeded. Builds and publishes the package to PyPI.

### `publish_documentation` Job

```yaml
jobs:
  publish_documentation:
    runs-on: ubuntu-latest
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    steps:
      # ... steps here
```

Runs on `ubuntu-latest` only if release workflow succeeded. Builds and deploys documentation to GitHub Pages.

## Steps

### Steps for `publish_package` Job

#### 1. Checkout Repository

```yaml
- name: Checkout Repository
  id: checkout_repository
  uses: actions/checkout@main
```

Checks out repository code for building

#### 2. Setup Git

```yaml
- name: Setup Git
  id: setup_git
  run: |
    git config --global user.email "github-actions[bot]@users.noreply.github.com"
    git config --global user.name "github-actions[bot]"
```

Configures git identity (standard setup step)

#### 3. Setup Project Management

```yaml
- name: Setup Project Mgt
  id: setup_project_mgt
  uses: astral-sh/setup-uv@main
  with:
    python-version: '3.14'
```

Installs uv and the latest Python version allowed by `requires-python` constraint (currently 3.14)

#### 4. Build Wheel

```yaml
- name: Build Wheel
  id: build_wheel
  run: uv build
```

Builds wheel (`.whl`) and source distribution (`.tar.gz`) in `dist/` directory

#### 5. Publish To PyPI

```yaml
- name: Publish To Pypi
  id: publish_to_pypi
  run: 'if [ ${{ secrets.PYPI_TOKEN != '''' }} ]; then uv publish --token ${{ secrets.PYPI_TOKEN }}; else echo "Skipping step due to failed condition: secrets.PYPI_TOKEN != ''''."; fi'
```

**Conditional logic:** Bash conditional checks if `PYPI_TOKEN` is configured
- Token exists: Publishes to PyPI
- Token missing: Prints skip message and succeeds

### Steps for `publish_documentation` Job

#### 1. Checkout Repository

```yaml
- name: Checkout Repository
  id: checkout_repository
  uses: actions/checkout@main
```

Checks out repository code for building documentation

#### 2. Setup Git

```yaml
- name: Setup Git
  id: setup_git
  run: |
    git config --global user.email "github-actions[bot]@users.noreply.github.com"
    git config --global user.name "github-actions[bot]"
```

Configures git identity for committing to gh-pages branch

#### 3. Setup Project Management

```yaml
- name: Setup Project Mgt
  id: setup_project_mgt
  uses: astral-sh/setup-uv@main
  with:
    python-version: '3.14'
```

Installs uv and the latest Python version allowed by `requires-python` constraint (currently 3.14)

#### 4. Patch Version

```yaml
- name: Patch Version
  id: patch_version
  run: uv version --bump patch && git add pyproject.toml
```

Bumps the patch version in `pyproject.toml` and stages the change

#### 5. Install Python Dependencies

```yaml
- name: Install Python Dependencies
  id: install_python_dependencies
  run: uv lock --upgrade && uv sync
```

Updates and installs all Python dependencies (including documentation dependencies like mkdocs and mkdocs-mermaid2-plugin)

#### 6. Add Dependency Updates To Git

```yaml
- name: Add Dependency Updates To Git
  id: add_dependency_updates_to_git
  run: git add pyproject.toml uv.lock
```

Stages the updated dependency files

#### 7. Build Documentation

```yaml
- name: Build Documentation
  id: build_documentation
  run: uv mkdocs build
```

Builds the MkDocs documentation into the `site/` directory

#### 8. Publish Documentation

```yaml
- name: Publish Documentation
  id: publish_documentation
  uses: peaceiris/actions-gh-pages@main
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    publish_dir: site
```

Deploys the built documentation to the `gh-pages` branch using the `peaceiris/actions-gh-pages` action

**Note:** After the first deployment, you need to manually configure GitHub Pages in your repository settings:
1. Go to **Settings → Pages**
2. Under **Build and deployment**, set **Source** to **Deploy from a branch**
3. Select the **gh-pages** branch
4. Click **Save**

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
permissions:
  contents: write
run-name: Publish
defaults:
  run:
    shell: bash
env:
  PYTHONDONTWRITEBYTECODE: 1
  UV_NO_SYNC: 1
jobs:
  publish_package:
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
      run: 'if [ ${{ secrets.PYPI_TOKEN != '''' }} ]; then uv publish --token ${{ secrets.PYPI_TOKEN }}; else echo "Skipping step due to failed condition: secrets.PYPI_TOKEN != ''''."; fi'
  publish_documentation:
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
    - name: Patch Version
      id: patch_version
      run: uv version --bump patch && git add pyproject.toml
    - name: Install Python Dependencies
      id: install_python_dependencies
      run: uv lock --upgrade && uv sync
    - name: Add Dependency Updates To Git
      id: add_dependency_updates_to_git
      run: git add pyproject.toml uv.lock
    - name: Build Documentation
      id: build_documentation
      run: uv mkdocs build
    - name: Publish Documentation
      id: publish_documentation
      uses: peaceiris/actions-gh-pages@main
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: site
```

## Required Secrets

### `PYPI_TOKEN`

**Required:** No (optional - publish command is skipped if not configured)

**Behavior:** Uses bash conditional - if token exists, publishes; if missing, prints skip message and succeeds.

**Setup:**

1. **Create PyPI account** at [pypi.org](https://pypi.org)
2. **Generate API token:**
   - Go to Account Settings → API tokens
   - Click "Add API token"
   - Name: `GitHub Actions`
   - Scope: Entire account (or specific project after first publish)
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

Triggers after release workflow completes successfully. Runs two parallel jobs:
1. **publish_package**: Builds wheel and publishes to PyPI
2. **publish_documentation**: Builds documentation and deploys to GitHub Pages

### Manual Execution

Go to Actions → Publish → Run workflow (useful for republishing, updating documentation, or testing)

## Monitoring

View workflow runs in GitHub Actions → Publish. Check if package is published with `pip index versions <package>` or visit PyPI.

## Customization

You can customize the workflow by subclassing:

```python
# my_awesome_project/dev/configs/workflows/publish.py
from pyrig.dev.configs.workflows.publish import PublishWorkflow
from typing import Any


class CustomPublishWorkflow(PublishWorkflow):
    """Custom publish workflow with additional steps."""

    @classmethod
    def steps_publish_package(cls) -> list[dict[str, Any]]:
        """Add custom steps to publishing."""
        return [
            *super().steps_publish_package(),
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

### Issue: Want to publish but seeing skip message

**Symptom:** Publish step shows: `"Skipping step due to failed condition: secrets.PYPI_TOKEN != ''"`

**Solution:** Add `PYPI_TOKEN` secret (see [Required Secrets](#required-secrets) section above)

### Issue: Package already exists on PyPI

PyPI doesn't allow overwriting versions. Bump version with `uv version --bump patch`, commit, and push.

### Issue: Workflow doesn't trigger

Check release workflow status in Actions. If release succeeded but publish didn't trigger, manually run it from Actions → Publish → Run workflow.

### Issue: Build fails

Test build locally with `uv build`. Fix any errors in `pyproject.toml` or missing files.

### Issue: Publish fails with authentication error

Generate new PyPI token at pypi.org → Account Settings → API tokens, then update `PYPI_TOKEN` secret in GitHub.

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
            run=f"uv publish --token {cls.insert_var('secrets.TEST_PYPI_TOKEN')} --publish-url https://test.pypi.org/legacy/",
            step=step,
        )
```

Then add `TEST_PYPI_TOKEN` secret with token from [test.pypi.org](https://test.pypi.org).

## Best Practices

- Use API tokens (more secure than username/password)
- Scope tokens to specific projects when possible
- Test locally with `uv build` before pushing
- Never commit tokens - always use GitHub secrets
- Don't skip version bumps - PyPI won't accept duplicates
- Let the workflow handle publishing (don't publish manually)

## Advanced Usage

### Conditional Publishing

```python
# my_awesome_project/dev/configs/workflows/publish.py
from pyrig.dev.configs.workflows.publish import PublishWorkflow
from typing import Any


class CustomPublishWorkflow(PublishWorkflow):
    """Only publish on main branch."""

    @classmethod
    def job_publish_package(cls) -> dict[str, Any]:
        """Add branch condition."""
        job = super().job_publish_package()
        job["publish_package"]["if"] = "${{ github.ref == 'refs/heads/main' && github.event.workflow_run.conclusion == 'success' }}"
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
    def steps_publish_package(cls) -> list[dict[str, Any]]:
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
            run=f"uv publish --token {cls.insert_var('secrets.PRIVATE_INDEX_TOKEN')} --publish-url https://private.example.com/simple/",
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


