# WorkflowConfigFile Architecture

GitHub Actions workflows for CI/CD automation in pyrig projects.

## Overview

Pyrig provides a declarative API for building GitHub Actions workflows through
the `WorkflowConfigFile` base class. All workflow config files inherit from this
class and generate YAML files in `.github/workflows/`.

## Inheritance Hierarchy

```mermaid
graph TD
    A[ConfigFile] --> B[YamlConfigFile]
    B --> B1[YmlConfigFile]
    B1 --> C[WorkflowConfigFile]
    C --> D[HealthCheckWorkflowConfigFile]
    C --> E[BuildWorkflowConfigFile]
    C --> F[ReleaseWorkflowConfigFile]
    C --> G[DeployWorkflowConfigFile]

    style A fill:#a8dadc,stroke:#333,stroke-width:2px,color:#000
    style B fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    style B1 fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    style C fill:#e76f51,stroke:#333,stroke-width:2px,color:#000
    style D fill:#90be6d,stroke:#333,stroke-width:2px,color:#000
    style E fill:#90be6d,stroke:#333,stroke-width:2px,color:#000
    style F fill:#90be6d,stroke:#333,stroke-width:2px,color:#000
    style G fill:#90be6d,stroke:#333,stroke-width:2px,color:#000
```

## WorkflowConfigFile Base Class

The `WorkflowConfigFile` class provides:

### Core Structure

- **Jobs**: Define workflow jobs with dependencies, strategies, and steps
- **Steps**: Individual actions or shell commands within jobs
- **Triggers**: Events that start the workflow (push, PR, schedule,
  workflow_run)
- **Permissions**: GitHub token permissions for the workflow
- **Matrix Strategies**: Run jobs across OS and Python version combinations

### WorkflowConfigFile Lifecycle

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
    ArtifactsUploaded --> WorkflowConfigFileComplete: All jobs done
    JobSuccess --> WorkflowConfigFileComplete: No artifacts
    JobFailure --> WorkflowConfigFileFailed
    WorkflowConfigFileComplete --> [*]
    WorkflowConfigFileFailed --> [*]

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
class MyWorkflowConfigFile(WorkflowConfigFile):
    @classmethod
    def jobs(cls) -> dict[str, Any]:
        return cls.job(
            job_func=cls.jobs,
            runs_on=cls.UBUNTU_LATEST,
            steps=[
                cls.step_checkout_repository(),
                cls.step_setup_package_manager(python_version="3.12"),
                cls.step_run_tests(),
            ]
        )
```

### Naming Conventions

- **WorkflowConfigFile name**: Generated from class name
(e.g., `HealthCheckWorkflowConfigFile` → `"Health Check"`)
- **Job IDs**: Generated from method names (e.g., `job_matrix_health_checks` →
  `"matrix_health_checks"`)
- **Step IDs**: Generated from method names (e.g., `step_run_tests` →
  `"run_tests"`)

### Opt-Out Mechanism

WorkflowConfigFiles can be opted out by replacing all steps with
`step_opt_out_of_workflow()`. This creates a valid workflow that never runs,
allowing users to disable workflows without deleting files. Or if you empty the
file it will be regenerated on next `uv run pyrig mkroot` with the opt-out steps
for you. So just empty the file and run `uv run pyrig mkroot` to opt out.

## Concrete WorkflowConfigFiles

Pyrig provides four workflows that form a complete CI/CD pipeline:

```mermaid
graph LR
    A[Code Push/PR] --> B[Health Check]
    S[Schedule/Cron] --> B
    B -->|Success on main<br/>not cron| C[Build]
    C -->|Success| D[Release]
    D -->|Success| E[Deploy]

    B -.->|Jobs| B1[health_checks<br/>matrix_health_checks<br/>health_check]
    C -.->|Jobs| C1[build_artifacts<br/>build_container_image]
    D -.->|Jobs| D1[release]
    E -.->|Jobs| E1[publish_package<br/>deploy_documentation]

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

### 1. Health Check WorkflowConfigFile

**File**: `.github/workflows/health_check.yml`

**Triggers**:

- Pull requests
- Pushes to main
- Scheduled (daily, staggered by dependency depth)

**Jobs**:

- **health_checks**: Runs quality checks and applies branch protection rules
  - Prek checks (ruff lint/format, ty, bandit, rumdl)
  - Dependency security audit (pip-audit)
- **matrix_health_checks**: Runs across OS (Ubuntu, Windows, macOS) and Python
  versions
  - Tests with coverage (pytest)
  - Coverage upload (codecov)
- **health_check**: Aggregates health_checks and matrix_health_checks results
  (required status check for PRs)

**Purpose**: Continuous integration - ensures code quality on every change.

### 2. Build WorkflowConfigFile

**File**: `.github/workflows/build.yml`

**Triggers**:

- After health check completes successfully on main
- Excludes cron-triggered health checks (only push/dispatch triggers build)

**Jobs**:

- **build_artifacts**: Builds project artifacts across OS matrix
- **build_container_image**: Builds container image (Ubuntu only)

**Purpose**: Creates distributable artifacts after CI passes.

### 3. Release WorkflowConfigFile

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

### 4. Deploy WorkflowConfigFile

**File**: `.github/workflows/deploy.yml`

**Triggers**:

- After release workflow completes successfully

**Jobs**:

- **publish_package**: Publishes to PyPI
  - Builds wheel
  - Publishes with PYPI_TOKEN (if configured)
- **deploy_documentation**: Deploys to GitHub Pages
  - Builds MkDocs site
  - Uploads and deploys to Pages

**Permissions**: `pages: write`, `id-token: write` (for docs job)

**Purpose**: Distributes package and documentation.

## Creating Custom WorkflowConfigFiles

To create your own workflow, subclass `WorkflowConfigFile` and implement `jobs()`:

```python
# myapp/rig/configs/workflows/custom.py
from typing import Any
from pyrig.rig.configs.base.workflow import WorkflowConfigFile

class CustomWorkflowConfigFile(WorkflowConfigFile):
    """Custom workflow that runs on push and manual trigger."""

    @classmethod
    def workflow_triggers(cls) -> dict[str, Any]:
        """Trigger on push and manual dispatch."""
        triggers = super().workflow_triggers()
        triggers.update(cls.on_push())
        return triggers

    @classmethod
    def jobs(cls) -> dict[str, Any]:
        """Define the workflow jobs."""
        jobs: dict[str, Any] = {}
        jobs.update(cls.job_custom_task())
        return jobs

    @classmethod
    def job_custom_task(cls) -> dict[str, Any]:
        """Custom job that runs a script."""
        return cls.job(
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
