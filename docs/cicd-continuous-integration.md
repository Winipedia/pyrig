# CI/CD (Continuous Integration/Continuous Deployment)

pyrig provides a complete CI/CD pipeline through auto-generated GitHub Actions workflows. The system includes health checks, automated releases, and PyPI publishing, all configured through Python classes.

## Overview

pyrig's CI/CD system consists of three chained workflows:

1. **Health Check Workflow** — Runs tests and quality checks across multiple OS and Python versions
2. **Release Workflow** — Creates version tags and GitHub releases after successful health checks
3. **Publish Workflow** — Publishes the package to PyPI after successful releases

Key characteristics:

- **Auto-generated** — Workflow YAML files are generated from Python classes
- **Matrix testing** — Tests run on Ubuntu, Windows, and macOS with Python 3.12, 3.13, and 3.14
- **Chained execution** — Each workflow triggers the next upon successful completion
- **Branch protection** — Automated repository protection rules enforce code quality
- **Pre-commit integration** — CI runs the same pre-commit hooks as local development

## Pipeline Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CI/CD Pipeline                                  │
└─────────────────────────────────────────────────────────────────────────────┘

  Pull Request / Push to main / Scheduled
                    │
                    ▼
    ┌───────────────────────────────┐
    │    Health Check Workflow      │
    │  ┌─────────────────────────┐  │
    │  │   Matrix: 3 OS × 3 Py   │  │
    │  │   • Ubuntu + 3.12/13/14 │  │
    │  │   • Windows + 3.12/13/14│  │
    │  │   • macOS + 3.12/13/14  │  │
    │  └─────────────────────────┘  │
    │  Steps:                       │
    │  • Checkout                   │
    │  • Setup uv                   │
    │  • Install dependencies       │
    │  • Patch version              │
    │  • Update dependencies        │
    │  • Protect repository         │
    │  • Run pre-commit hooks       │
    │  • Run tests                  │
    └───────────────────────────────┘
                    │
                    │ (on main branch, success)
                    ▼
    ┌───────────────────────────────┐
    │      Release Workflow         │
    │  Jobs:                        │
    │  • Build artifacts (matrix)   │
    │  • Create version tag         │
    │  • Generate changelog         │
    │  • Create GitHub release      │
    └───────────────────────────────┘
                    │
                    │ (success)
                    ▼
    ┌───────────────────────────────┐
    │      Publish Workflow         │
    │  Steps:                       │
    │  • Build wheel                │
    │  • Publish to PyPI            │
    └───────────────────────────────┘
```

## Workflow Files

The workflows are defined as Python classes that generate YAML files:

| Workflow Class | Generated File | Purpose |
|----------------|----------------|---------|
| `HealthCheckWorkflow` | `.github/workflows/health_check.yaml` | CI testing and quality checks |
| `ReleaseWorkflow` | `.github/workflows/release.yaml` | Version tagging and GitHub releases |
| `PublishWorkflow` | `.github/workflows/publish.yaml` | PyPI publishing |

## Health Check Workflow

The health check workflow is the primary CI workflow that validates code quality.

### Triggers

- **Pull requests** — Runs on opened, synchronized, and reopened PRs
- **Push to main** — Runs when code is pushed to the main branch
- **Scheduled** — Runs daily via cron (staggered based on dependency depth)

### Matrix Strategy

Tests run across a matrix of operating systems and Python versions:

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
```

This creates 9 parallel jobs (3 OS × 3 Python versions).

### Steps

Each matrix job executes these steps:

1. **Checkout Repository** — Clone the repository
2. **Setup Project Mgt** — Install uv package manager
3. **Install Python Dependencies** — Run `uv sync`
4. **Patch Version** — Bump patch version with `uv version --bump patch`
5. **Update Dependencies** — Run `uv lock --upgrade && uv sync`
6. **Add Dependency Updates To Git** — Stage changes with `git add pyproject.toml uv.lock`
7. **Protect Repository** — Apply branch protection rules (requires `REPO_TOKEN`)
8. **Run Pre Commit Hooks** — Execute `uv run pre-commit run --all-files`
9. **Run Tests** — Execute `uv run pytest --log-cli-level=INFO`

### Aggregation Job

After all matrix jobs complete, an aggregation job runs to provide a single status check:

```yaml
health_check:
  needs:
    - health_check_matrix
  runs-on: ubuntu-latest
  steps:
    - name: Aggregate Matrix Results
      run: echo 'Aggregating matrix results into one job.'
```

This allows branch protection rules to require a single status check rather than all 9 matrix jobs.

### Staggered Scheduling

Packages that depend on pyrig have their scheduled runs staggered to avoid conflicts:

```python
@classmethod
def get_staggered_cron(cls) -> str:
    offset = cls.get_dependency_offset()
    base_time = datetime.now(tz=UTC).replace(hour=cls.BASE_CRON_HOUR, ...)
    scheduled_time = base_time + timedelta(hours=offset)
    return f"0 {scheduled_time.hour} * * *"
```

The offset is calculated based on the shortest path length in the dependency graph to pyrig.

## Release Workflow

The release workflow creates version tags and GitHub releases.

### Trigger

Triggers when the Health Check Workflow completes successfully on the main branch:

```yaml
on:
  workflow_run:
    workflows:
      - Health Check Workflow
    types:
      - completed
    branches:
      - main
```

### Jobs

**Build Job** (matrix across OS):
- Runs only if health check succeeded
- Builds artifacts using custom `Builder` subclasses
- Uploads artifacts for the release

**Release Job**:
1. Checkout with `REPO_TOKEN` for push permissions
2. Setup git identity for commits
3. Run pre-commit hooks
4. Commit any changes (e.g., version bump)
5. Push commits to main
6. Create and push version tag
7. Download build artifacts
8. Generate changelog from PR history
9. Create GitHub release with artifacts

## Publish Workflow

The publish workflow publishes the package to PyPI.

### Trigger

Triggers when the Release Workflow completes successfully:

```yaml
on:
  workflow_run:
    workflows:
      - Release Workflow
    types:
      - completed
```

### Steps

1. **Checkout Repository** — Clone the repository
2. **Setup Project Mgt** — Install uv with Python 3.14
3. **Build Wheel** — Run `uv build`
4. **Publish To PyPI** — Run `uv publish --token ${{ secrets.PYPI_TOKEN }}`

## Branch Protection

pyrig automatically configures branch protection rules via the `protect-repo` command.

### Repository Settings

The following repository settings are applied:

| Setting | Value | Purpose |
|---------|-------|---------|
| `default_branch` | `main` | Standard branch name |
| `delete_branch_on_merge` | `true` | Clean up merged branches |
| `allow_update_branch` | `true` | Enable "Update branch" button |
| `allow_merge_commit` | `false` | Disable merge commits |
| `allow_rebase_merge` | `true` | Allow rebase merging |
| `allow_squash_merge` | `true` | Allow squash merging |

### Branch Ruleset

A ruleset named "main protection" is created with these rules:

| Rule | Configuration |
|------|---------------|
| **Pull Request Required** | 1 approving review, code owner review required, dismiss stale reviews |
| **Status Checks** | Health Check Workflow must pass |
| **Linear History** | Required (no merge commits) |
| **Signed Commits** | Required |
| **No Force Push** | Enabled |
| **No Deletion** | Enabled |

### Pull Request Requirements

```python
pull_request={
    "required_approving_review_count": 1,
    "dismiss_stale_reviews_on_push": True,
    "require_code_owner_review": True,
    "require_last_push_approval": True,
    "required_review_thread_resolution": True,
    "allowed_merge_methods": ["squash", "rebase"],
}
```

## Required Secrets

Configure these secrets in your GitHub repository settings:

| Secret | Purpose | Where to Get |
|--------|---------|--------------|
| `REPO_TOKEN` | GitHub API access for branch protection and commits | GitHub Settings → Developer settings → Personal access tokens |
| `PYPI_TOKEN` | PyPI publishing | PyPI Account → API tokens |

### REPO_TOKEN Permissions

The `REPO_TOKEN` needs these permissions:

- `repo` — Full control of private repositories
- `workflow` — Update GitHub Action workflows

### Local Development

For local development, add `REPO_TOKEN` to your `.env` file:

```
REPO_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

The `get_github_repo_token()` function checks:
1. `REPO_TOKEN` environment variable (for CI)
2. `.env` file (for local development)

## Workflow Classes

### Base Class: `Workflow`

All workflow classes inherit from `Workflow`, which provides:

```python
class Workflow(YamlConfigFile):
    """Abstract base class for GitHub Actions workflow configuration."""

    UBUNTU_LATEST = "ubuntu-latest"
    WINDOWS_LATEST = "windows-latest"
    MACOS_LATEST = "macos-latest"

    @classmethod
    @abstractmethod
    def get_jobs(cls) -> dict[str, Any]:
        """Subclasses must implement this to define their jobs."""

    @classmethod
    def get_workflow_triggers(cls) -> dict[str, Any]:
        """Override to customize when the workflow runs."""

    @classmethod
    def get_permissions(cls) -> dict[str, Any]:
        """Override to request additional permissions."""
```

### Key Methods

| Method | Purpose |
|--------|---------|
| `get_job()` | Build a job configuration |
| `get_step()` | Build a step configuration |
| `strategy_matrix_os_and_python_version()` | Create OS × Python matrix |
| `on_push()` | Create push trigger |
| `on_pull_request()` | Create PR trigger |
| `on_workflow_run()` | Create workflow completion trigger |
| `on_schedule()` | Create cron schedule trigger |

### Step Builders

The `Workflow` class provides pre-built steps:

| Method | Generated Step |
|--------|----------------|
| `step_checkout_repository()` | Checkout with actions/checkout |
| `step_setup_project_mgt()` | Setup uv with astral-sh/setup-uv |
| `step_install_python_dependencies()` | Run `uv sync` |
| `step_run_tests()` | Run `uv run pytest` |
| `step_run_pre_commit_hooks()` | Run `uv run pre-commit run --all-files` |
| `step_protect_repository()` | Run `uv run pyrig protect-repo` |
| `step_build_wheel()` | Run `uv build` |
| `step_publish_to_pypi()` | Run `uv publish` |

## Customizing Workflows

### Creating a Custom Workflow

Create a new workflow by subclassing `Workflow`:

```python
# your_project/dev/configs/workflows/deploy.py
from typing import Any
from pyrig.dev.configs.workflows.base.base import Workflow

class DeployWorkflow(Workflow):
    """Custom deployment workflow."""

    @classmethod
    def get_workflow_triggers(cls) -> dict[str, Any]:
        triggers = super().get_workflow_triggers()
        triggers.update(cls.on_push(branches=["main"]))
        return triggers

    @classmethod
    def get_jobs(cls) -> dict[str, Any]:
        return cls.get_job(
            job_func=cls.job_deploy,
            steps=[
                cls.step_checkout_repository(),
                cls.step_setup_project_mgt(),
                cls.step_deploy(),
            ],
        )

    @classmethod
    def job_deploy(cls) -> dict[str, Any]:
        """Deploy job configuration."""
        pass  # Used for naming only

    @classmethod
    def step_deploy(cls) -> dict[str, Any]:
        return cls.get_step(
            step_func=cls.step_deploy,
            run="./deploy.sh",
        )
```

### Overriding Built-in Workflows

To customize the health check workflow:

```python
# your_project/dev/configs/workflows/health_check.py
from pyrig.dev.configs.workflows.health_check import HealthCheckWorkflow as Base

class HealthCheckWorkflow(Base):
    """Customized health check with additional steps."""

    @classmethod
    def steps_health_check_matrix(cls) -> list[dict[str, Any]]:
        steps = super().steps_health_check_matrix()
        steps.append(cls.step_custom_check())
        return steps

    @classmethod
    def step_custom_check(cls) -> dict[str, Any]:
        return cls.get_step(
            step_func=cls.step_custom_check,
            run="./custom-check.sh",
        )
```

## Regenerating Workflows

After modifying workflow classes, regenerate the YAML files:

```bash
uv run pyrig build
```

This updates all files in `.github/workflows/`.

## File Structure

```
your_project/
├── .github/
│   └── workflows/
│       ├── health_check.yaml    # Generated
│       ├── release.yaml         # Generated
│       └── publish.yaml         # Generated
├── your_project/
│   └── dev/
│       └── configs/
│           └── workflows/
│               ├── __init__.py
│               └── custom.py    # Your custom workflows
└── pyproject.toml
```

## Troubleshooting

### "Resource not accessible by integration"

**Cause**: The `REPO_TOKEN` doesn't have sufficient permissions.

**Solution**: Create a new personal access token with `repo` and `workflow` scopes.

### "PYPI_TOKEN not found"

**Cause**: The PyPI token secret is not configured.

**Solution**:
1. Go to PyPI → Account settings → API tokens
2. Create a token scoped to your project
3. Add it as a repository secret named `PYPI_TOKEN`

### Health check passes but release doesn't trigger

**Cause**: The release workflow only triggers on the main branch.

**Solution**: Ensure you're pushing to main, not a feature branch.

### Pre-commit hooks fail in CI but pass locally

**Cause**: Different tool versions or missing dependencies.

**Solution**:
1. Run `uv lock --upgrade` locally
2. Commit the updated `uv.lock`
3. Ensure all pre-commit hooks are in `.pre-commit-config.yaml`

### Matrix job fails on one OS only

**Cause**: OS-specific behavior or path differences.

**Solution**:
1. Check for hardcoded paths (use `pathlib.Path`)
2. Check for OS-specific commands
3. Review the failed job logs in GitHub Actions

### Branch protection prevents pushing

**Cause**: The ruleset requires PRs for all changes.

**Solution**:
1. Create a feature branch
2. Open a PR
3. Get approval and pass status checks
4. Merge via squash or rebase

## Summary

| Component | Description |
|-----------|-------------|
| **Health Check** | Matrix testing across 3 OS × 3 Python versions |
| **Release** | Automated version tagging and GitHub releases |
| **Publish** | PyPI publishing with `uv publish` |
| **Branch Protection** | Enforced reviews, status checks, and linear history |
| **Secrets** | `REPO_TOKEN` for GitHub API, `PYPI_TOKEN` for PyPI |
| **Customization** | Subclass `Workflow` to add or modify workflows |

