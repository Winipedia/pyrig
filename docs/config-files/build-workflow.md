# BuildWorkflow

## Overview

**File Location:** `.github/workflows/build.yaml`
**ConfigFile Class:** `BuildWorkflow`
**File Type:** YAML (GitHub Actions Workflow)
**Priority:** Standard

GitHub Actions workflow that builds distributable artifacts across multiple operating systems after successful health checks on the main branch. Creates Python wheels, source distributions, and container images ready for release.

## Purpose

The build workflow serves as the artifact creation pipeline in pyrig's CI/CD system:

- **Cross-Platform Builds** - Creates artifacts on Ubuntu, Windows, and macOS
- **Dependency Updates** - Upgrades dependencies to latest versions before building
- **Version Bumping** - Automatically increments patch version for each build
- **Container Images** - Builds Podman/Docker container images
- **Artifact Storage** - Uploads all artifacts for the release workflow to use

### Why pyrig manages this file

The build workflow ensures:
1. **Reproducible builds** across all major operating systems
2. **Up-to-date dependencies** via automatic upgrades before building
3. **Automated versioning** without manual intervention
4. **Container support** for modern deployment workflows
5. **Artifact preservation** for release automation

The workflow is created during `pyrig init` and updated by `pyrig mkroot`. It only runs after the health check workflow succeeds on the main branch, ensuring only tested code is built.

## Workflow Triggers

### `workflow_run`

- **Type:** object
- **Default:** Triggers on `Health Check` workflow completion on `main` branch
- **Required:** Yes
- **Purpose:** Ensures builds only happen after successful health checks
- **Why pyrig sets it:** Prevents building broken code; health checks must pass first

Configuration:
```yaml
workflow_run:
  workflows:
    - Health Check
  types:
    - completed
  branches:
    - main
```

### `workflow_dispatch`

- **Type:** object
- **Default:** `{}` (enabled with no inputs)
- **Required:** No
- **Purpose:** Allows manual triggering from GitHub UI
- **Why pyrig sets it:** Enables manual builds when needed for testing or special releases

## Workflow Configuration

### `name`

- **Type:** string
- **Default:** `"Build"`
- **Required:** Yes
- **Purpose:** Display name in GitHub Actions UI
- **Why pyrig sets it:** Clear, concise name for the workflow

### `permissions`

- **Type:** object
- **Default:** `{}` (no special permissions)
- **Required:** No
- **Purpose:** Defines GitHub token permissions
- **Why pyrig sets it:** Follows principle of least privilege; uses default permissions

### `run-name`

- **Type:** string
- **Default:** `"Build"`
- **Required:** No
- **Purpose:** Display name for individual workflow runs
- **Why pyrig sets it:** Consistent naming for workflow runs

### `defaults.run.shell`

- **Type:** string
- **Default:** `"bash"`
- **Required:** No
- **Purpose:** Default shell for all run steps
- **Why pyrig sets it:** Ensures consistent shell behavior across all platforms (including Windows)

### `env`

Global environment variables for all jobs:

#### `PYTHONDONTWRITEBYTECODE`

- **Type:** string (number)
- **Default:** `"1"`
- **Required:** No
- **Purpose:** Prevents Python from writing .pyc files
- **Why pyrig sets it:** Keeps build environment clean; .pyc files not needed in CI

#### `UV_NO_SYNC`

- **Type:** string (number)
- **Default:** `"1"`
- **Required:** No
- **Purpose:** Prevents uv from auto-syncing dependencies
- **Why pyrig sets it:** Explicit control over when dependencies are installed

## Jobs

### `build_artifacts`

Builds Python packages (wheels and source distributions) across all major operating systems.

#### `strategy.matrix.os`

- **Type:** array of strings
- **Default:** `["ubuntu-latest", "windows-latest", "macos-latest"]`
- **Required:** Yes
- **Purpose:** Operating systems to build on
- **Why pyrig sets it:** Ensures artifacts work on all major platforms

#### `strategy.fail-fast`

- **Type:** boolean
- **Default:** `true`
- **Required:** No
- **Purpose:** Stop all matrix jobs if one fails
- **Why pyrig sets it:** Saves CI minutes; if build fails on one OS, likely fails on others

#### `runs-on`

- **Type:** string (matrix expression)
- **Default:** `${{ matrix.os }}`
- **Required:** Yes
- **Purpose:** Specifies which runner to use
- **Why pyrig sets it:** Uses matrix value to run on each OS

#### `if`

- **Type:** string (expression)
- **Default:** `${{ github.event.workflow_run.conclusion == 'success' }}`
- **Required:** Yes (for workflow_run trigger)
- **Purpose:** Only run if health check succeeded
- **Why pyrig sets it:** Prevents building code that failed health checks

#### Steps for `build_artifacts`

1. **Checkout Repository** - Clones the repository
2. **Setup Git** - Configures git user for commits
3. **Setup Project Mgt** - Installs uv with latest allowed Python version
4. **Patch Version** - Bumps patch version (e.g., 1.2.3 → 1.2.4)
5. **Install Python Dependencies** - Upgrades and installs all dependencies
6. **Add Dependency Updates To Git** - Stages updated lock file
7. **Build Artifacts** - Runs `uv run pyrig build` to create wheels/sdist
8. **Upload Artifacts** - Uploads to GitHub Actions artifacts storage

### `build_container_image`

Builds a Podman container image from the Containerfile.

#### `runs-on`

- **Type:** string
- **Default:** `"ubuntu-latest"`
- **Required:** Yes
- **Purpose:** Specifies which runner to use
- **Why pyrig sets it:** Container builds only need one OS; Ubuntu has best Podman support

#### `if`

- **Type:** string (expression)
- **Default:** `${{ github.event.workflow_run.conclusion == 'success' }}`
- **Required:** Yes (for workflow_run trigger)
- **Purpose:** Only run if health check succeeded
- **Why pyrig sets it:** Prevents building containers from broken code

#### Steps for `build_container_image`

1. **Checkout Repository** - Clones the repository
2. **Install Container Engine** - Installs Podman via redhat-actions/podman-install
3. **Build Container Image** - Runs `podman build -t <project-name> .`
4. **Make Dist Folder** - Creates `dist/` directory
5. **Save Container Image** - Saves image as `dist/<project-name>.tar`
6. **Upload Artifacts** - Uploads container image with name `container-image`

## Step Details

### Checkout Repository

```yaml
- name: Checkout Repository
  id: checkout_repository
  uses: actions/checkout@main
```

- **Purpose:** Clones the repository code to the runner
- **Action:** `actions/checkout@main`
- **Why needed:** All subsequent steps need access to the code

### Setup Git

```yaml
- name: Setup Git
  id: setup_git
  run: git config --global user.email "github-actions[bot]@users.noreply.github.com"
    && git config --global user.name "github-actions[bot]"
```

- **Purpose:** Configures git identity for commits
- **Why needed:** Version bumping and dependency updates create commits that need a git identity

### Setup Project Mgt

```yaml
- name: Setup Project Mgt
  id: setup_project_mgt
  uses: astral-sh/setup-uv@main
  with:
    python-version: '3.14'
```

Installs uv and the latest Python version allowed by `requires-python` constraint (currently 3.14)

### Patch Version

```yaml
- name: Patch Version
  id: patch_version
  run: uv version --bump patch && git add pyproject.toml
```

- **Purpose:** Automatically increments the patch version number
- **Example:** `1.2.3` → `1.2.4`
- **Why needed:** Each build on main gets a unique version number for releases
- **Note:** Changes are staged but not committed (release workflow commits them)

### Install Python Dependencies

```yaml
- name: Install Python Dependencies
  id: install_python_dependencies
  run: uv lock --upgrade && uv sync
```

- **Purpose:** Updates dependencies to latest versions and installs them
- **Commands:**
  - `uv lock --upgrade` - Updates `uv.lock` with latest compatible versions
  - `uv sync` - Installs dependencies from the updated lock file
- **Why needed:** Ensures builds use the latest dependency versions

### Add Dependency Updates To Git

```yaml
- name: Add Dependency Updates To Git
  id: add_dependency_updates_to_git
  run: git add pyproject.toml uv.lock
```

- **Purpose:** Stages dependency changes for commit
- **Files staged:** `pyproject.toml` (version bump) and `uv.lock` (dependency updates)
- **Why needed:** Release workflow will commit these changes

### Build Artifacts

```yaml
- name: Build Artifacts
  id: build_artifacts
  run: uv run pyrig build
```

- **Purpose:** Builds Python wheels and source distributions
- **Command:** `uv run pyrig build`
- **Output:** Creates files in `dist/` directory
- **What's built:**
  - Wheel (`.whl`) - Binary distribution
  - Source distribution (`.tar.gz`) - Source code archive
  - Any custom artifacts from builders in `<package>/dev/builders/`
- **Why needed:** Creates distributable packages for PyPI and releases

### Upload Artifacts

```yaml
- name: Upload Artifacts
  id: upload_artifacts
  uses: actions/upload-artifact@main
  with:
    name: pyrig-${{ runner.os }}
    path: dist
```

- **Purpose:** Uploads build artifacts to GitHub Actions storage
- **Action:** `actions/upload-artifact@main`
- **Artifact name:** `<project-name>-<OS>` (e.g., `pyrig-Linux`, `pyrig-Windows`, `pyrig-macOS`)
- **Path:** `dist/` directory containing all built artifacts
- **Why needed:** Release workflow downloads these artifacts to create GitHub releases and publish to PyPI

### Install Container Engine

```yaml
- name: Install Container Engine
  id: install_container_engine
  uses: redhat-actions/podman-install@main
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
```

- **Purpose:** Installs Podman container engine
- **Action:** `redhat-actions/podman-install@main`
- **Why Podman:** Daemonless, rootless, Docker-compatible container engine (user preference)
- **Why needed:** Required to build container images

### Build Container Image

```yaml
- name: Build Container Image
  id: build_container_image
  run: podman build -t pyrig .
```

- **Purpose:** Builds a container image from the Containerfile
- **Command:** `podman build -t <project-name> .`
- **Tag:** Uses project name as image tag
- **Context:** Current directory (`.`)
- **Why needed:** Creates containerized version of the application

### Make Dist Folder

```yaml
- name: Make Dist Folder
  id: make_dist_folder
  run: mkdir -p dist
```

- **Purpose:** Ensures `dist/` directory exists
- **Why needed:** Container image will be saved to this directory

### Save Container Image

```yaml
- name: Save Container Image
  id: save_container_image
  run: podman save -o dist/pyrig.tar pyrig
```

- **Purpose:** Exports container image to a tar archive
- **Command:** `podman save -o dist/<project-name>.tar <project-name>`
- **Output:** `dist/<project-name>.tar` file
- **Why needed:** Allows container image to be uploaded as an artifact and used in releases

## Default Configuration

Here's the complete build workflow for a project named `pyrig`:

```yaml
name: Build
'on':
  workflow_dispatch: {}
  workflow_run:
    workflows:
    - Health Check
    types:
    - completed
    branches:
    - main
permissions: {}
run-name: Build
defaults:
  run:
    shell: bash
env:
  PYTHONDONTWRITEBYTECODE: 1
  UV_NO_SYNC: 1
jobs:
  build_artifacts:
    strategy:
      matrix:
        os:
        - ubuntu-latest
        - windows-latest
        - macos-latest
      fail-fast: true
    runs-on: ${{ matrix.os }}
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
    - name: Build Artifacts
      id: build_artifacts
      run: uv run pyrig build
    - name: Upload Artifacts
      id: upload_artifacts
      uses: actions/upload-artifact@main
      with:
        name: pyrig-${{ runner.os }}
        path: dist
  build_container_image:
    runs-on: ubuntu-latest
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    steps:
    - name: Checkout Repository
      id: checkout_repository
      uses: actions/checkout@main
    - name: Install Container Engine
      id: install_container_engine
      uses: redhat-actions/podman-install@main
      with:
        github-token: ${{ secrets.GITHUB_TOKEN }}
    - name: Build Container Image
      id: build_container_image
      run: podman build -t pyrig .
    - name: Make Dist Folder
      id: make_dist_folder
      run: mkdir -p dist
    - name: Save Container Image
      id: save_container_image
      run: podman save -o dist/pyrig.tar pyrig
    - name: Upload Artifacts
      id: upload_artifacts
      uses: actions/upload-artifact@main
      with:
        name: container-image
        path: dist
```

## Customization

You can customize this workflow by subclassing `BuildWorkflow` and overriding specific methods.

### Example: Build on Fewer Operating Systems

If you only need Linux builds:

```python
from pyrig.dev.configs.workflows.build import BuildWorkflow


class CustomBuildWorkflow(BuildWorkflow):
    @classmethod
    def job_build_artifacts(cls) -> dict[str, Any]:
        """Build only on Ubuntu."""
        return cls.get_job(
            job_func=cls.job_build_artifacts,
            if_condition=cls.if_workflow_run_is_success(),
            strategy=cls.strategy_matrix_os(os=["ubuntu-latest"]),
            runs_on=cls.insert_matrix_os(),
            steps=cls.steps_build_artifacts(),
        )
```

### Example: Skip Container Image Build

If you don't need container images:

```python
from pyrig.dev.configs.workflows.build import BuildWorkflow


class CustomBuildWorkflow(BuildWorkflow):
    @classmethod
    def get_jobs(cls) -> dict[str, Any]:
        """Only build artifacts, skip container image."""
        jobs: dict[str, Any] = {}
        jobs.update(cls.job_build_artifacts())
        # Don't include job_build_container_image
        return jobs
```

### Example: Add Custom Build Step

To add a custom step after building:

```python
from typing import Any
from pyrig.dev.configs.workflows.build import BuildWorkflow


class CustomBuildWorkflow(BuildWorkflow):
    @classmethod
    def steps_build_artifacts(cls) -> list[dict[str, Any]]:
        """Add custom validation step."""
        return [
            *cls.steps_core_matrix_setup(),
            cls.step_build_artifacts(),
            cls.get_step(
                step_func=lambda: None,
                name="Validate Artifacts",
                run="uv run python scripts/validate_build.py",
            ),
            cls.step_upload_artifacts(),
        ]
```

## Workflow Execution Flow

### Trigger Sequence

1. **Developer pushes to main** (or PR is merged)
2. **Health Check workflow runs** - Lints, type checks, tests across OS/Python matrix
3. **Health Check succeeds** - All checks pass
4. **Build workflow triggers** - `workflow_run` event fires
5. **Build jobs run in parallel:**
   - `build_artifacts` runs on 3 OS simultaneously
   - `build_container_image` runs on Ubuntu
6. **Artifacts uploaded** - All builds upload to GitHub Actions storage
7. **Release workflow can now run** - Uses these artifacts

### Timing

- **Typical duration:** 5-10 minutes total
  - `build_artifacts`: 3-5 minutes per OS (parallel)
  - `build_container_image`: 2-4 minutes
- **Parallelization:** Both jobs run simultaneously, matrix builds run in parallel
- **Cost:** Uses GitHub Actions minutes (free tier: 2000 min/month for public repos)

### Conditional Execution

The workflow only runs when:
- ✅ Health Check workflow completes on `main` branch
- ✅ Health Check workflow conclusion is `success`
- ❌ Does NOT run on pull requests
- ❌ Does NOT run on feature branches
- ❌ Does NOT run if health checks fail

### Artifact Outputs

After successful completion, the following artifacts are available:

1. **`<project-name>-Linux`** - Linux wheel and sdist
2. **`<project-name>-Windows`** - Windows wheel
3. **`<project-name>-macOS`** - macOS wheel
4. **`container-image`** - Container image tar file

These artifacts are:
- Stored for 90 days by default
- Downloaded by the release workflow
- Used to create GitHub releases
- Published to PyPI (wheels and sdist)
- Attached to GitHub releases (container image)

## Related Files

- **`.github/workflows/health-check.yaml`** - Must succeed before this workflow runs
- **`.github/workflows/release.yaml`** - Downloads artifacts from this workflow
- **`Containerfile`** - Defines the container image build
- **`<package>/dev/builders/`** - Custom builder classes for additional artifacts
- **`pyproject.toml`** - Version is bumped by this workflow
- **`uv.lock`** - Updated with latest dependencies by this workflow

## Common Issues

### Issue: Build workflow doesn't trigger after merging PR

**Symptom:** Health check passes but build workflow never starts

**Cause:** The `workflow_run` trigger only fires when the triggering workflow completes on the specified branch (`main`)

**Solution:**
- Ensure you merged to `main`, not pushed to a feature branch
- Check that the health check workflow actually ran on `main`
- Verify the health check workflow name matches exactly: `"Health Check"`
- Check GitHub Actions tab for any workflow run errors

### Issue: Build fails with "No builders defined"

**Symptom:** Build step completes but no artifacts are created

**Cause:** No builder classes exist in `<package>/dev/builders/`

**Solution:**
This is actually normal for simple projects. The default behavior is:
- If no custom builders exist, `pyrig build` creates standard wheel and sdist
- The message is informational, not an error
- If you want custom artifacts, create builder classes in `<package>/dev/builders/`

### Issue: Container image build fails

**Symptom:** `build_container_image` job fails with Podman errors

**Cause:** Usually an issue with the Containerfile

**Solution:**
1. Test the Containerfile locally: `podman build -t myproject .`
2. Check that the Containerfile exists in the project root
3. Verify all files referenced in the Containerfile exist
4. Check Podman installation step succeeded
5. Review the build logs for specific error messages

### Issue: Version bump creates conflicts

**Symptom:** Release workflow fails because version was already bumped

**Cause:** Multiple builds running simultaneously or manual version changes

**Solution:**
- Don't manually change version in `pyproject.toml` - let the workflow handle it
- Ensure only one build runs at a time (fail-fast helps with this)
- If conflicts occur, the release workflow should handle them gracefully

### Issue: Dependency upgrade breaks build

**Symptom:** Build succeeds but artifacts don't work due to dependency issues

**Cause:** `uv lock --upgrade` updated a dependency to a breaking version

**Solution:**
1. Pin the problematic dependency in `pyproject.toml`:
   ```toml
   dependencies = [
       "problematic-package<2.0",  # Pin to avoid breaking changes
   ]
   ```
2. Run `uv lock` locally to update the lock file
3. Commit and push the updated `pyproject.toml` and `uv.lock`
4. Future builds will respect the pin

**Prevention:** Use semantic versioning constraints in dependencies

### Issue: Artifacts too large

**Symptom:** Upload fails or takes very long

**Cause:** Build creates very large artifacts (>1GB)

**Solution:**
1. Review what's being included in the build
2. Check `.gitignore` and build exclusions
3. Consider splitting large assets into separate artifacts
4. Use artifact retention policies to clean up old artifacts

### Issue: Matrix build fails on one OS

**Symptom:** Build succeeds on Linux but fails on Windows or macOS

**Cause:** Platform-specific code or dependencies

**Solution:**
1. Test locally on the failing platform if possible
2. Add platform-specific dependencies in `pyproject.toml`:
   ```toml
   dependencies = [
       "windows-specific-package; sys_platform == 'win32'",
   ]
   ```
3. Use platform checks in code:
   ```python
   import sys
   if sys.platform == "win32":
       # Windows-specific code
   ```
4. Review the build logs for platform-specific errors

## Secrets Required

### `GITHUB_TOKEN`

- **Type:** Automatic secret (provided by GitHub)
- **Purpose:** Used by Podman installation action
- **Scope:** Read access to repository
- **Why needed:** The `redhat-actions/podman-install` action requires authentication

**Note:** This is automatically provided by GitHub Actions - you don't need to configure it.

## See Also

- [Health Check Workflow](health-check-workflow.md) - Prerequisite workflow
- [Release Workflow](release-workflow.md) - Consumes artifacts from this workflow
- [Containerfile](container-file.md) - Container image definition
- [Getting Started Guide](../getting-started.md) - Initial project setup
- [GitHub Actions Documentation](https://docs.github.com/en/actions) - Official GitHub Actions docs
- [workflow_run Trigger](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#workflow_run) - Understanding workflow_run events


