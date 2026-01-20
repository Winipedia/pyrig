# Workflow Architecture

GitHub Actions workflows for CI/CD automation in pyrig projects.

## Overview

Pyrig provides a declarative API for building GitHub Actions workflows through
the `Workflow` base class. All workflow config files inherit from this class and
generate YAML files in `.github/workflows/`.

## Inheritance Hierarchy

```mermaid
graph TD
    A[ConfigFile] --> B[YamlConfigFile]
    B --> C[Workflow]
    C --> D[HealthCheckWorkflow]
    C --> E[BuildWorkflow]
    C --> F[ReleaseWorkflow]
    C --> G[PublishWorkflow]

    style A fill:#a8dadc,stroke:#333,stroke-width:2px,color:#000
    style B fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    style C fill:#e76f51,stroke:#333,stroke-width:2px,color:#000
    style D fill:#90be6d,stroke:#333,stroke-width:2px,color:#000
    style E fill:#90be6d,stroke:#333,stroke-width:2px,color:#000
    style F fill:#90be6d,stroke:#333,stroke-width:2px,color:#000
    style G fill:#90be6d,stroke:#333,stroke-width:2px,color:#000
```

## Workflow Base Class

The `Workflow` class provides:

### Core Structure

- **Jobs**: Define workflow jobs with dependencies, strategies, and steps
- **Steps**: Individual actions or shell commands within jobs
- **Triggers**: Events that start the workflow (push, PR, schedule,
  workflow_run)
- **Permissions**: GitHub token permissions for the workflow
- **Matrix Strategies**: Run jobs across OS and Python version combinations

### Workflow Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Triggered
    Triggered --> JobsQueued: Event matches trigger
    JobsQueued --> JobRunning: Runner available
    JobRunning --> StepsExecuting: Job starts
    StepsExecuting --> StepSuccess: Step completes
    StepSuccess --> StepsExecuting: More steps
    StepSuccess --> JobSuccess: All steps done
    StepsExecuting --> StepFailure: Step fails
    StepFailure --> JobFailure
    JobSuccess --> ArtifactsUploaded: Has artifacts
    ArtifactsUploaded --> WorkflowComplete: All jobs done
    JobSuccess --> WorkflowComplete: No artifacts
    JobFailure --> WorkflowFailed
    WorkflowComplete --> [*]
    WorkflowFailed --> [*]

    note right of Triggered
        Triggers: push, pull_request,
        schedule, workflow_run,
        workflow_dispatch
    end note

    note right of StepsExecuting
        Steps: checkout, setup,
        install, test, build,
        upload, etc.
    end note
```

### Declarative API

Instead of writing YAML manually, you define workflows in Python:

```python
class MyWorkflow(Workflow):
    @classmethod
    def get_jobs(cls) -> dict[str, Any]:
        return cls.get_job(
            job_func=cls.my_job,
            runs_on=cls.UBUNTU_LATEST,
            steps=[
                cls.step_checkout_repository(),
                cls.step_setup_package_manager(python_version="3.12"),
                cls.step_run_tests(),
            ]
        )
```

### Naming Conventions

- **Workflow name**: Generated from class name (e.g., `HealthCheckWorkflow` →
  `"Health Check"`)
- **Job IDs**: Generated from method names (e.g., `job_health_check_matrix` →
  `"health_check_matrix"`)
- **Step IDs**: Generated from method names (e.g., `step_run_tests` →
  `"run_tests"`)

### Opt-Out Mechanism

Workflows can be opted out by replacing all steps with
`step_opt_out_of_workflow()`. This creates a valid workflow that never runs,
allowing users to disable workflows without deleting files. Or if you empty the
file it will be regenerated on next `uv run pyrig mkroot` with the opt-out steps
for you. So just empty the file and run `uv run pyrig mkroot` to opt out.

## Concrete Workflows

Pyrig provides four workflows that form a complete CI/CD pipeline:

```mermaid
graph LR
    A[Code Push/PR] --> B[Health Check]
    S[Schedule/Cron] --> B
    B -->|Success on main<br/>not cron| C[Build]
    C -->|Success| D[Release]
    D -->|Success| E[Publish]

    B -.->|Jobs| B1[health_checks<br/>matrix_health_checks<br/>health_check]
    C -.->|Jobs| C1[build_artifacts<br/>build_container_image]
    D -.->|Jobs| D1[release]
    E -.->|Jobs| E1[publish_package<br/>publish_documentation]

    B1 -.->|Outputs| B2[Code quality validated<br/>Branch protection applied]
    C1 -.->|Outputs| C2[Executables<br/>Container image]
    D1 -.->|Outputs| D2[Git tag<br/>GitHub release]
    E1 -.->|Outputs| E2[PyPI package<br/>GitHub Pages docs]

    style A fill:#a8dadc,stroke:#333,stroke-width:2px,color:#000
    style B fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    style C fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    style D fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    style E fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    style B2 fill:#90be6d,stroke:#333,stroke-width:1px,color:#000
    style C2 fill:#90be6d,stroke:#333,stroke-width:1px,color:#000
    style D2 fill:#90be6d,stroke:#333,stroke-width:1px,color:#000
    style E2 fill:#90be6d,stroke:#333,stroke-width:1px,color:#000
```

### 1. Health Check Workflow

**File**: `.github/workflows/health_check.yml`

**Triggers**:

- Pull requests
- Pushes to main
- Scheduled (daily, staggered by dependency depth)

**Jobs**:

- **health_checks**: Runs quality checks and applies branch protection rules
  - Pre-commit checks (ruff lint/format, ty, bandit, rumdl)
  - Dependency security audit (pip-audit)
- **matrix_health_checks**: Runs across OS (Ubuntu, Windows, macOS) and Python
  versions
  - Tests with coverage (pytest)
  - Coverage upload (codecov)
- **health_check**: Aggregates health_checks and matrix_health_checks results
  (required status check for PRs)

**Purpose**: Continuous integration - ensures code quality on every change.

### 2. Build Workflow

**File**: `.github/workflows/build.yml`

**Triggers**:

- After health check completes successfully on main
- Excludes cron-triggered health checks (only push/dispatch triggers build)

**Jobs**:

- **build_artifacts**: Builds project artifacts across OS matrix
- **build_container_image**: Builds container image (Ubuntu only)

**Purpose**: Creates distributable artifacts after CI passes.

### 3. Release Workflow

**File**: `.github/workflows/release.yml`

**Triggers**:

- After build workflow completes successfully

**Jobs**:

- **release**: Creates GitHub release
  - Bumps patch version
  - Commits and pushes changes
  - Creates and pushes git tag
  - Downloads artifacts from build workflow
  - Generates changelog
  - Creates GitHub release with artifacts

**Permissions**: `contents: write`, `actions: read`

**Purpose**: Automates versioning and GitHub releases.

### 4. Publish Workflow

**File**: `.github/workflows/publish.yml`

**Triggers**:

- After release workflow completes successfully

**Jobs**:

- **publish_package**: Publishes to PyPI
  - Builds wheel
  - Publishes with PYPI_TOKEN (if configured)
- **publish_documentation**: Publishes to GitHub Pages
  - Builds MkDocs site
  - Uploads and deploys to Pages

**Permissions**: `pages: write`, `id-token: write` (for docs job)

**Purpose**: Distributes package and documentation.

## Creating Custom Workflows

To create your own workflow, subclass `Workflow` and implement `get_jobs()`:

```python
# myapp/dev/configs/workflows/custom.py
from typing import Any
from pyrig.dev.configs.base.workflow import Workflow

class CustomWorkflow(Workflow):
    """Custom workflow that runs on manual trigger."""

    @classmethod
    def get_workflow_triggers(cls) -> dict[str, Any]:
        """Trigger manually via workflow_dispatch."""
        triggers = super().get_workflow_triggers()
        triggers.update(cls.on_workflow_dispatch())
        return triggers

    @classmethod
    def get_jobs(cls) -> dict[str, Any]:
        """Define the workflow jobs."""
        jobs: dict[str, Any] = {}
        jobs.update(cls.job_custom_task())
        return jobs

    @classmethod
    def job_custom_task(cls) -> dict[str, Any]:
        """Custom job that runs a script."""
        return cls.get_job(
            job_func=cls.job_custom_task,
            runs_on=cls.UBUNTU_LATEST,
            steps=[
                cls.step_checkout_repository(),
                cls.step_setup_version_control(),
                cls.step_setup_package_manager(python_version="3.12"),
                cls.step_install_dependencies(),
                {
                    "name": "Run custom script",
                    "run": "uv run python scripts/custom_task.py",
                },
            ],
        )
```

After creating the file, run `uv run pyrig mkroot` to generate
`.github/workflows/custom.yml`.

## Best Practices

1. **Don't edit YAML directly**: Modify the Python workflow classes instead by
   subclassing them as you can with all ConfigFiles
2. **Use opt-out for customization**: Replace steps with
   `step_opt_out_of_workflow()` to disable
3. **Configure secrets**: Add REPO_TOKEN, PYPI_TOKEN, CODECOV_TOKEN to
   repository secrets (see
   [Getting Started](../../more/getting-started.md#accounts--tokens))
4. **Test locally**: Run `uv run pyrig mkroot` to regenerate workflows after
   changes
