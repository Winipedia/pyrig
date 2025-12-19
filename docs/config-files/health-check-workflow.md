# HealthCheckWorkflow

## Overview

**File Location:** `.github/workflows/health_check.yaml`
**ConfigFile Class:** `HealthCheckWorkflow`
**File Type:** YAML (GitHub Actions Workflow)
**Priority:** Standard

Runs continuous integration health checks on pull requests, pushes to main, and scheduled intervals. Tests code across a matrix of operating systems and Python versions to ensure cross-platform compatibility.

## Purpose

The `.github/workflows/health_check.yaml` workflow provides comprehensive CI/CD validation:

- **Pull Request Validation** - Runs on every PR to catch issues early
- **Main Branch Protection** - Validates code before it reaches production
- **Scheduled Testing** - Daily runs catch dependency breakage
- **Cross-Platform Testing** - Tests on Ubuntu, Windows, and macOS
- **Multi-Version Testing** - Tests across all supported Python versions
- **Quality Gates** - Linting, type checking, security scanning, and tests

### Why pyrig manages this workflow

pyrig creates `health_check.yaml` to:
1. **Immediate CI/CD** - Working CI from day one
2. **Best practices** - Comprehensive quality checks
3. **Cross-platform** - Ensures code works everywhere
4. **Dependency management** - Automatic dependency updates
5. **Staggered scheduling** - Avoids conflicts with dependency releases

The workflow is created during `pyrig init` and updated by `pyrig mkroot`. It runs before the build workflow to ensure only tested code is built.

## Workflow Triggers

### `pull_request`

- **Type:** object
- **Default:** Triggers on `opened`, `synchronize`, `reopened`
- **Required:** Yes
- **Purpose:** Validates code changes before merging
- **Why pyrig sets it:** Catches issues in PRs before they reach main

Configuration:
```yaml
pull_request:
  types:
    - opened
    - synchronize
    - reopened
```

**When it runs:**
- **opened** - When a PR is first created
- **synchronize** - When new commits are pushed to the PR
- **reopened** - When a closed PR is reopened

### `push`

- **Type:** object
- **Default:** Triggers on pushes to `main` branch
- **Required:** Yes
- **Purpose:** Validates code after merging to main
- **Why pyrig sets it:** Ensures main branch always passes health checks

Configuration:
```yaml
push:
  branches:
    - main
```

**When it runs:**
- After a PR is merged to main
- After a direct push to main (if allowed)

### `schedule`

- **Type:** array of cron expressions
- **Default:** Daily at staggered time based on dependency depth
- **Required:** Yes
- **Purpose:** Catches dependency breakage and security issues
- **Why pyrig sets it:** Dependencies can break between releases

Configuration:
```yaml
schedule:
  - cron: "0 0 * * *"  # Daily at midnight UTC (for pyrig)
```

**Staggered Scheduling:**
Pyrig uses dependency depth to stagger scheduled runs:
- **pyrig** - Runs at hour 0 (midnight UTC)
- **Packages depending on pyrig** - Run at hour 1
- **Packages depending on those** - Run at hour 2
- And so on...

This prevents conflicts when dependencies release right before dependent packages run their health checks.

### `workflow_dispatch`

- **Type:** object
- **Default:** Empty object (allows manual triggering)
- **Required:** Yes
- **Purpose:** Allows manual workflow execution
- **Why pyrig sets it:** Useful for debugging and testing

Configuration:
```yaml
workflow_dispatch: {}
```

**How to use:**
1. Go to Actions tab in GitHub
2. Select "Health Check" workflow
3. Click "Run workflow"
4. Select branch and click "Run workflow"

## Workflow Configuration

### `name`

- **Type:** string
- **Default:** `"Health Check"`
- **Required:** Yes
- **Purpose:** Workflow display name in GitHub UI
- **Why pyrig sets it:** Clear identification in Actions tab

### `permissions`

- **Type:** object
- **Default:** `{}` (no permissions)
- **Required:** Yes
- **Purpose:** Restricts workflow permissions for security
- **Why pyrig sets it:** Principle of least privilege

The workflow uses repository secrets for authentication instead of workflow permissions.

### `run-name`

- **Type:** string
- **Default:** `"Health Check"`
- **Required:** Yes
- **Purpose:** Display name for workflow runs
- **Why pyrig sets it:** Clear identification in run history

### `defaults`

- **Type:** object
- **Default:** Sets bash as default shell
- **Required:** Yes
- **Purpose:** Ensures consistent shell across all platforms
- **Why pyrig sets it:** Windows uses PowerShell by default; bash is more portable

Configuration:
```yaml
defaults:
  run:
    shell: bash
```

### `env`

- **Type:** object
- **Default:** Sets Python and uv environment variables
- **Required:** Yes
- **Purpose:** Configures Python and package manager behavior
- **Why pyrig sets it:** Optimizes performance and prevents issues

Configuration:
```yaml
env:
  PYTHONDONTWRITEBYTECODE: 1
  UV_NO_SYNC: 1
```

**Environment variables:**
- **PYTHONDONTWRITEBYTECODE: 1** - Prevents `.pyc` file creation (faster, cleaner)
- **UV_NO_SYNC: 1** - Prevents automatic `uv sync` (we control when it runs)

## Jobs

The workflow has two jobs that run sequentially:

### `health_check_matrix`

- **Type:** Matrix job
- **Purpose:** Runs health checks across OS and Python version combinations
- **Runs on:** Ubuntu, Windows, macOS
- **Python versions:** All supported versions (3.12, 3.13, 3.14)
- **Strategy:** Fail-fast enabled (stops on first failure)

**Matrix configuration:**
```yaml
strategy:
  matrix:
    os:
      - ubuntu-latest
      - windows-latest
      - macos-latest
    python-version:
      - '3.12'
      - '3.13'
      - '3.14'
  fail-fast: true
runs-on: ${{ matrix.os }}
```

**Total combinations:** 9 (3 OS × 3 Python versions)

All 9 combinations run in parallel for fast feedback.

### `health_check`

- **Type:** Aggregation job
- **Purpose:** Aggregates matrix results into single job
- **Depends on:** `health_check_matrix`
- **Runs on:** Ubuntu latest
- **Why:** Provides single status check for branch protection

**Configuration:**
```yaml
health_check:
  needs: [health_check_matrix]
  steps:
    - name: Aggregate Matrix Results
      run: echo 'Aggregating matrix results into one job.'
```

**Why aggregation is needed:**
GitHub branch protection can require a single status check. The aggregation job provides this single check that depends on all matrix jobs succeeding.

## Steps (health_check_matrix job)

### 1. Checkout Repository

```yaml
- name: Checkout Repository
  uses: actions/checkout@main
```

- **Purpose:** Clones the repository code
- **Action:** `actions/checkout@main`
- **Why:** Needed to access code for testing

### 2. Setup Git

```yaml
- name: Setup Git
  run: |
    git config --global user.email "github-actions[bot]@users.noreply.github.com"
    git config --global user.name "github-actions[bot]"
```

- **Purpose:** Configures Git for commits
- **Why:** Version patching and dependency updates create commits

### 3. Setup Project Mgt

```yaml
- name: Setup Project Mgt
  uses: astral-sh/setup-uv@main
  with:
    python-version: ${{ matrix.python-version }}
```

- **Purpose:** Installs uv and Python
- **Action:** `astral-sh/setup-uv@main`
- **Python version:** From matrix (3.12, 3.13, or 3.14)
- **Why:** uv is the package manager; Python is needed to run code

### 4. Patch Version

```yaml
- name: Patch Version
  run: uv version --bump patch && git add pyproject.toml
```

- **Purpose:** Increments patch version
- **Why:** Every health check run gets a new version number
- **Example:** `1.0.0` → `1.0.1`

### 5. Install Python Dependencies

```yaml
- name: Install Python Dependencies
  run: uv lock --upgrade && uv sync
```

- **Purpose:** Updates and installs dependencies
- **Commands:**
  - `uv lock --upgrade` - Updates `uv.lock` with latest compatible versions
  - `uv sync` - Installs dependencies from lock file
- **Why:** Ensures latest dependencies are tested

### 6. Add Dependency Updates To Git

```yaml
- name: Add Dependency Updates To Git
  run: git add pyproject.toml uv.lock
```

- **Purpose:** Stages dependency changes
- **Why:** Prepares for potential commit

### 7. Protect Repository

```yaml
- name: Protect Repository
  run: uv run pyrig protect-repo
  env:
    REPO_TOKEN: ${{ secrets.REPO_TOKEN }}
```

- **Purpose:** Applies repository protection rules
- **Command:** `pyrig protect-repo`
- **Secret:** `REPO_TOKEN` (GitHub PAT with repo permissions)
- **Why:** Ensures branch protection and required checks are configured

### 8. Run Pre Commit Hooks

```yaml
- name: Run Pre Commit Hooks
  run: uv run pre-commit run --all-files
```

- **Purpose:** Runs all pre-commit hooks
- **Checks:**
  - ruff (linting and formatting)
  - mypy (type checking)
  - bandit (security scanning)
  - And more (see `.pre-commit-config.yaml`)
- **Why:** Catches code quality issues

### 9. Run Tests

```yaml
- name: Run Tests
  run: uv run pytest --log-cli-level=INFO --cov-report=xml
  env:
    REPO_TOKEN: ${{ secrets.REPO_TOKEN }}
```

- **Purpose:** Runs test suite with coverage
- **Command:** `pytest --log-cli-level=INFO --cov-report=xml`
- **Options:**
  - `--log-cli-level=INFO` - Shows INFO logs in output
  - `--cov-report=xml` - Generates coverage.xml for Codecov
- **Why:** Validates code correctness and coverage

### 10. Upload Coverage Report

```yaml
- name: Upload Coverage Report
  if: ${{ secrets.CODECOV_TOKEN != '' }}
  uses: codecov/codecov-action@main
  with:
    files: coverage.xml
    token: ${{ secrets.CODECOV_TOKEN }}
    fail_ci_if_error: 'true'
```

- **Purpose:** Uploads coverage to Codecov
- **Action:** `codecov/codecov-action@main`
- **File:** `coverage.xml` (generated by pytest)
- **Secret:** `CODECOV_TOKEN` (optional - step skipped if not configured)
- **Conditional:** Step only runs if `CODECOV_TOKEN` is configured
- **Why:** Tracks coverage trends over time

**Note:** This step is automatically skipped if `CODECOV_TOKEN` is not configured. When the token is present, the step will fail the workflow if the upload fails (`fail_ci_if_error: true`).

## Default Configuration

For a project named `my-awesome-project`:

**File location:** `.github/workflows/health_check.yaml`

**Complete workflow:**
```yaml
name: Health Check
on:
  workflow_dispatch: {}
  pull_request:
    types:
      - opened
      - synchronize
      - reopened
  push:
    branches:
      - main
  schedule:
    - cron: "0 1 * * *"  # Staggered based on dependency depth
permissions: {}
run-name: Health Check
defaults:
  run:
    shell: bash
env:
  PYTHONDONTWRITEBYTECODE: 1
  UV_NO_SYNC: 1
jobs:
  health_check_matrix:
    strategy:
      matrix:
        os:
          - ubuntu-latest
          - windows-latest
          - macos-latest
        python-version:
          - '3.12'
          - '3.13'
          - '3.14'
      fail-fast: true
    runs-on: ${{ matrix.os }}
    steps:
      - name: Checkout Repository
        uses: actions/checkout@main
      - name: Setup Git
        run: |
          git config --global user.email "github-actions[bot]@users.noreply.github.com"
          git config --global user.name "github-actions[bot]"
      - name: Setup Project Mgt
        uses: astral-sh/setup-uv@main
        with:
          python-version: ${{ matrix.python-version }}
      - name: Patch Version
        run: uv version --bump patch && git add pyproject.toml
      - name: Install Python Dependencies
        run: uv lock --upgrade && uv sync
      - name: Add Dependency Updates To Git
        run: git add pyproject.toml uv.lock
      - name: Protect Repository
        run: uv run pyrig protect-repo
        env:
          REPO_TOKEN: ${{ secrets.REPO_TOKEN }}
      - name: Run Pre Commit Hooks
        run: uv run pre-commit run --all-files
      - name: Run Tests
        run: uv run pytest --log-cli-level=INFO --cov-report=xml
        env:
          REPO_TOKEN: ${{ secrets.REPO_TOKEN }}
      - name: Upload Coverage Report
        if: ${{ secrets.CODECOV_TOKEN != '' }}
        uses: codecov/codecov-action@main
        with:
          files: coverage.xml
          token: ${{ secrets.CODECOV_TOKEN }}
          fail_ci_if_error: 'true'
  health_check:
    needs: [health_check_matrix]
    runs-on: ubuntu-latest
    steps:
      - name: Aggregate Matrix Results
        run: echo 'Aggregating matrix results into one job.'
```

## Workflow Execution Flow

### Trigger Sequence

1. **Developer creates PR** or **pushes to main** or **scheduled time arrives**
2. **Workflow starts** - All 9 matrix jobs start in parallel
3. **Matrix jobs run:**
   - Ubuntu + Python 3.12
   - Ubuntu + Python 3.13
   - Ubuntu + Python 3.14
   - Windows + Python 3.12
   - Windows + Python 3.13
   - Windows + Python 3.14
   - macOS + Python 3.12
   - macOS + Python 3.13
   - macOS + Python 3.14
4. **All matrix jobs must succeed**
5. **Aggregation job runs** - Provides single status check
6. **Workflow completes** - PR can be merged or build workflow triggers

### Timing

**Typical duration:**
- **Matrix jobs:** 5-10 minutes (run in parallel)
- **Aggregation job:** < 1 minute
- **Total:** 5-10 minutes

**Scheduled runs:**
- **pyrig:** Daily at 00:00 UTC
- **Your project:** Daily at (00:00 + dependency_depth) UTC

## Required Secrets

### REPO_TOKEN

- **Type:** GitHub Personal Access Token (PAT)
- **Permissions:** `repo` (full repository access)
- **Purpose:** Allows `protect-repo` command to configure branch protection
- **Required:** Yes (for `protect-repo` step)
- **How to create:**
  1. Go to GitHub Settings → Developer settings → Personal access tokens
  2. Generate new token (classic)
  3. Select `repo` scope
  4. Copy token
  5. Add to repository secrets as `REPO_TOKEN`

### CODECOV_TOKEN

- **Type:** Codecov upload token
- **Purpose:** Uploads coverage reports to Codecov
- **Required:** No (optional - step is skipped if not configured)
- **Behavior:** If `CODECOV_TOKEN` is not set, the upload coverage step is automatically skipped
- **How to create:**
  1. Sign up at [codecov.io](https://codecov.io)
  2. Add your repository
  3. Copy upload token
  4. Add to repository secrets as `CODECOV_TOKEN`

**Note:** The workflow will complete successfully even without this token. The coverage upload step includes a conditional check (`if: ${{ secrets.CODECOV_TOKEN != '' }}`) that skips the step when the token is not configured.

## Customization

### Example: Skip Windows Testing

```python
# my_awesome_project/dev/configs/workflows/health_check.py
"""Custom health check workflow."""

from typing import Any
from pyrig.dev.configs.workflows.health_check import HealthCheckWorkflow


class CustomHealthCheckWorkflow(HealthCheckWorkflow):
    """Health check workflow without Windows."""

    @classmethod
    def strategy_matrix_os_and_python_version(cls) -> dict[str, Any]:
        """Get matrix strategy without Windows."""
        strategy = super().strategy_matrix_os_and_python_version()
        # Remove Windows from OS list
        strategy["matrix"]["os"] = [
            "ubuntu-latest",
            "macos-latest",
        ]
        return strategy
```

### Example: Test Only Latest Python

```python
# my_awesome_project/dev/configs/workflows/health_check.py
"""Custom health check workflow."""

from typing import Any
from pyrig.dev.configs.workflows.health_check import HealthCheckWorkflow
from pyrig.dev.configs.pyproject import PyprojectConfigFile


class CustomHealthCheckWorkflow(HealthCheckWorkflow):
    """Health check workflow with only latest Python."""

    @classmethod
    def strategy_matrix_os_and_python_version(cls) -> dict[str, Any]:
        """Get matrix strategy with only latest Python."""
        strategy = super().strategy_matrix_os_and_python_version()
        # Use only latest Python version
        latest = PyprojectConfigFile.get_latest_possible_python_version()
        strategy["matrix"]["python-version"] = [latest]
        return strategy
```

### Example: Custom Cron Schedule

```python
# my_awesome_project/dev/configs/workflows/health_check.py
"""Custom health check workflow."""

from pyrig.dev.configs.workflows.health_check import HealthCheckWorkflow


class CustomHealthCheckWorkflow(HealthCheckWorkflow):
    """Health check workflow with custom schedule."""

    @classmethod
    def get_staggered_cron(cls) -> str:
        """Run at 6 AM UTC instead of staggered time."""
        return "0 6 * * *"
```

## Related Files

- **`.github/workflows/build.yaml`** - Build workflow (runs after this) ([build-workflow.md](build-workflow.md))
- **`.pre-commit-config.yaml`** - Pre-commit hooks configuration ([pre-commit-config.md](pre-commit-config.md))
- **`pyproject.toml`** - Project configuration ([pyproject.md](pyproject.md))
- **`tests/conftest.py`** - Test configuration ([conftest.md](conftest.md))

## Common Issues

### Issue: Matrix job fails on Windows

**Symptom:** Tests pass on Ubuntu/macOS but fail on Windows

**Cause:** Path separator differences (`/` vs `\`)

**Solution:**
```python
# Use pathlib.Path for cross-platform paths
from pathlib import Path

# Good:
config_path = Path("config") / "settings.json"

# Bad:
config_path = "config/settings.json"  # Fails on Windows
```

### Issue: REPO_TOKEN secret not set

**Symptom:** `protect-repo` step fails with authentication error

**Cause:** `REPO_TOKEN` secret not configured

**Solution:**
```bash
# Create GitHub PAT with repo scope
# Add to repository secrets as REPO_TOKEN
```

Or skip the protect-repo step:
```python
# my_awesome_project/dev/configs/workflows/health_check.py
from pyrig.dev.configs.workflows.health_check import HealthCheckWorkflow


class CustomHealthCheckWorkflow(HealthCheckWorkflow):
    """Health check without protect-repo."""

    @classmethod
    def steps_health_check_matrix(cls) -> list[dict]:
        """Get steps without protect-repo."""
        steps = super().steps_health_check_matrix()
        # Remove protect-repo step
        return [s for s in steps if "protect" not in s.get("name", "").lower()]
```

### Issue: Want coverage tracking but step is being skipped

**Symptom:** Coverage upload step shows as skipped in workflow logs

**Cause:** `CODECOV_TOKEN` secret not configured in GitHub

**Solution:**

1. Sign up at [codecov.io](https://codecov.io)
2. Add your repository to Codecov
3. Copy the upload token
4. Add `CODECOV_TOKEN` to repository secrets

**Note:** As of pyrig 2.2.14+, the coverage upload step is automatically skipped when `CODECOV_TOKEN` is not configured. This prevents workflow failures and allows you to add coverage tracking later when you're ready.

### Issue: Pre-commit hooks fail

**Symptom:** "Run Pre Commit Hooks" step fails

**Cause:** Code doesn't pass linting/formatting/type checking

**Solution:**
```bash
# Run pre-commit locally before pushing
uv run pre-commit run --all-files

# Auto-fix issues
uv run pre-commit run --all-files --hook-stage manual

# Or let ruff fix automatically
uv run ruff check --fix .
uv run ruff format .
```

### Issue: Tests fail only in CI

**Symptom:** Tests pass locally but fail in GitHub Actions

**Cause:** Environment differences

**Solution:**
```python
# Check for CI environment
import os

if os.getenv("CI"):
    # CI-specific behavior
    pass

# Or use pytest markers
@pytest.mark.skipif(os.getenv("CI"), reason="Skips in CI")
def test_local_only():
    pass
```

## Best Practices

### ✅ DO

- **Run health checks locally** - Use `uv run pre-commit run --all-files`
- **Test on multiple OS** - Don't skip Windows/macOS testing
- **Keep tests fast** - Aim for < 5 minute test runs
- **Use matrix wisely** - Test all supported Python versions
- **Monitor scheduled runs** - Check for dependency breakage

### ❌ DON'T

- **Don't skip health checks** - They catch issues early
- **Don't ignore failures** - Fix them before merging
- **Don't hardcode paths** - Use pathlib for cross-platform compatibility
- **Don't skip coverage** - Maintain high coverage (90%+)
- **Don't disable fail-fast** - Catch failures quickly

## See Also

- [GitHub Actions Documentation](https://docs.github.com/en/actions) - Official docs
- [GitHub Actions Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions) - Workflow YAML reference
- [build.yaml](build-workflow.md) - Build workflow
- [pre-commit-config.yaml](pre-commit-config.md) - Pre-commit configuration
- [Getting Started Guide](../getting-started.md) - Initial project setup




