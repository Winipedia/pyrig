# health_check.yaml

Continuous integration workflow that validates code quality and runs tests.

## Overview

**File**: `.github/workflows/health_check.yaml`  
**Class**: `HealthCheckWorkflow` in `pyrig.dev.configs.workflows.health_check`  
**Inherits**: `Workflow`

The health check workflow is the first step in the CI/CD pipeline. It runs on
every pull request, push to main, and daily on a staggered schedule. It
validates code quality through linting, type checking, security scanning (code +
dependencies), and comprehensive testing across multiple OS and Python versions.

## Triggers

### Pull Request

- **Events**: `opened`, `synchronize`, `reopened`
- **Purpose**: Validate changes before merging

### Push

- **Branches**: `main`
- **Purpose**: Validate main branch after merge

### Schedule

- **Cron**: `0 {hour} * * *` (daily at staggered hour)
- **Staggering**: Hour offset based on dependency depth to pyrig
- **Purpose**: Catch issues from dependency updates

**Why staggered?** If your package depends on pyrig, and pyrig releases at
midnight, your package runs at 1 AM. This prevents failures when dependencies
release right before your scheduled run and keeps all packages up to date at the
same time if you have lots of packages depending in a line.

### Workflow Dispatch

- **Purpose**: Manual trigger for testing

## Job Flow

```mermaid
graph TD
    A[Trigger: PR/Push/Schedule] --> B[health_check_matrix]
    A --> P[protect_repository]
    B --> C[health_check]
    P --> C

    B --> B1[Ubuntu × Python 3.12]
    B --> B2[Ubuntu × Python 3.13]
    B --> B3[Ubuntu × Python 3.14]
    B --> B4[Windows × Python 3.12]
    B --> B5[Windows × Python 3.13]
    B --> B6[Windows × Python 3.14]
    B --> B7[macOS × Python 3.12]
    B --> B8[macOS × Python 3.13]
    B --> B9[macOS × Python 3.14]

    B1 --> C
    B2 --> C
    B3 --> C
    B4 --> C
    B5 --> C
    B6 --> C
    B7 --> C
    B8 --> C
    B9 --> C

    style A fill:#a8dadc,stroke:#333,stroke-width:2px,color:#000
    style B fill:#90be6d,stroke:#333,stroke-width:2px,color:#000
    style P fill:#9d84b7,stroke:#333,stroke-width:2px,color:#000
    style C fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    style B1 fill:#90be6d,stroke:#333,stroke-width:1px,color:#000
    style B2 fill:#90be6d,stroke:#333,stroke-width:1px,color:#000
    style B3 fill:#90be6d,stroke:#333,stroke-width:1px,color:#000
    style B4 fill:#90be6d,stroke:#333,stroke-width:1px,color:#000
    style B5 fill:#90be6d,stroke:#333,stroke-width:1px,color:#000
    style B6 fill:#90be6d,stroke:#333,stroke-width:1px,color:#000
    style B7 fill:#90be6d,stroke:#333,stroke-width:1px,color:#000
    style B8 fill:#90be6d,stroke:#333,stroke-width:1px,color:#000
    style B9 fill:#90be6d,stroke:#333,stroke-width:1px,color:#000
```

## Jobs

### 1. protect_repository

**Runs on**: Ubuntu latest
**Purpose**: Applies branch protection rules to the repository

This job runs independently from the test matrix to ensure branch protection is
configured before any code quality checks. It sets up the environment, updates
dependencies, and applies the branch protection ruleset from
`branch-protection.json`.

**Step Flow**:

```mermaid
graph TD
    P1[1. Checkout Repository] --> P2[2. Setup Git]
    P2 --> P3[3. Setup Project Mgt]
    P3 --> P4[4. Patch Version]
    P4 --> P5[5. Install Dependencies]
    P5 --> P6[6. Add Updates to Git]
    P6 --> P7[7. Protect Repository]

    P7 -.->|Loads| P7A[branch-protection.json]
    P7 -.->|Creates/Updates| P7B[GitHub Ruleset]
    P7 -.->|Requires| P7C[REPO_TOKEN]

    style P1 fill:#90be6d,stroke:#333,stroke-width:1px,color:#000
    style P2 fill:#90be6d,stroke:#333,stroke-width:1px,color:#000
    style P3 fill:#90be6d,stroke:#333,stroke-width:1px,color:#000
    style P4 fill:#90be6d,stroke:#333,stroke-width:1px,color:#000
    style P5 fill:#90be6d,stroke:#333,stroke-width:1px,color:#000
    style P6 fill:#90be6d,stroke:#333,stroke-width:1px,color:#000
    style P7 fill:#e76f51,stroke:#333,stroke-width:2px,color:#000
```

**Steps**:

1. **Checkout Repository** (`actions/checkout@main`)
   - Clones the repository code

2. **Setup Git**
   - Configures git user as `github-actions[bot]`
   - Required for version patching

3. **Setup Project Mgt** (`astral-sh/setup-uv@main`)
   - Installs uv package manager
   - Sets up Python 3.14

4. **Patch Version**
   - Bumps patch version in `pyproject.toml`
   - Stages change with `git add`

5. **Install Python Dependencies**
   - Updates lock file: `uv lock --upgrade`
   - Installs dependencies: `uv sync`

6. **Add Dependency Updates To Git**
   - Stages `pyproject.toml` and `uv.lock`

7. **Protect Repository**
   - Runs `uv run pyrig protect-repo`
   - Loads configuration from `branch-protection.json`
   - Creates or updates branch protection ruleset on GitHub
   - Requires `REPO_TOKEN` secret

**Why separate?** Running protection as a separate job ensures branch protection
is configured early in the workflow. The `health_check` aggregator job (which
waits for both this job and the matrix) is the required status check for PRs. No
need to call this in all matrix jobs.

### 2. health_check_matrix

**Runs on**: Matrix of OS × Python versions
**Strategy**: `fail-fast: true` (stop all jobs if one fails)
**Matrix**:

- **OS**: Ubuntu, Windows, macOS (latest)
- **Python**: All versions from `pyproject.toml` `requires-python` (e.g., 3.12,
  3.13, 3.14)

**Step Flow**:

```mermaid
graph TD
    S1[1. Checkout Repository] --> S2[2. Setup Git]
    S2 --> S3[3. Setup Project Mgt]
    S3 --> S4[4. Patch Version]
    S4 --> S5[5. Install Dependencies]
    S5 --> S6[6. Add Updates to Git]
    S6 --> S7[7. Run Pre-commit Hooks]
    S7 --> S8[8. Run Dependency Audit]
    S8 --> S9[9. Run Tests]
    S9 --> S10[10. Upload Coverage]

    style S1 fill:#90be6d,stroke:#333,stroke-width:1px,color:#000
    style S2 fill:#90be6d,stroke:#333,stroke-width:1px,color:#000
    style S3 fill:#90be6d,stroke:#333,stroke-width:1px,color:#000
    style S4 fill:#90be6d,stroke:#333,stroke-width:1px,color:#000
    style S5 fill:#90be6d,stroke:#333,stroke-width:1px,color:#000
    style S6 fill:#90be6d,stroke:#333,stroke-width:1px,color:#000
    style S7 fill:#e76f51,stroke:#333,stroke-width:1px,color:#000
    style S8 fill:#e76f51,stroke:#333,stroke-width:1px,color:#000
    style S9 fill:#e76f51,stroke:#333,stroke-width:1px,color:#000
    style S10 fill:#9d84b7,stroke:#333,stroke-width:1px,color:#000
```

**Steps**:

1. **Checkout Repository** (`actions/checkout@main`)
   - Clones the repository code

2. **Setup Git**
   - Configures git user as `github-actions[bot]`
   - Required for commits in later workflows

3. **Setup Project Mgt** (`astral-sh/setup-uv@main`)
   - Installs uv package manager
   - Sets up Python from matrix version

4. **Patch Version**
   - Bumps patch version in `pyproject.toml`
   - Stages change with `git add`
   - Ensures version is always ahead for releases

5. **Install Python Dependencies**
   - Updates lock file: `uv lock --upgrade`
   - Installs dependencies: `uv sync`
   - Tests against latest dependency versions

6. **Add Dependency Updates To Git**
   - Stages `pyproject.toml` and `uv.lock`
   - Prepares for potential commit in release workflow

7. **Run Pre Commit Hooks**
   - Runs `uv run pre-commit run --all-files`
   - Executes: ruff (linting), ty (type checking), bandit (security), rumdl
     (markdown linting)
   - Fails if any hook fails

    8. **Run Dependency Audit**
       - Runs `uv run pip-audit`
       - Scans installed dependencies for known vulnerabilities

    9. **Run Tests**
       - Runs `uv run pytest --log-cli-level=INFO --cov-report=xml`
       - Executes all tests with coverage measurement
       - Generates `coverage.xml` report
       - Requires 90% coverage (from `pyproject.toml`)

    10. **Upload Coverage Report** (`codecov/codecov-action@main`)
   - Uploads `coverage.xml` to Codecov
   - Uses `CODECOV_TOKEN` secret
   - Only fails CI if token is configured

**Why matrix?** Testing across OS and Python versions catches platform-specific
bugs and ensures compatibility.

### 3. health_check

**Runs on**: Ubuntu latest
**Needs**: `health_check_matrix`, `protect_repository` (waits for both to
complete)
**Purpose**: Aggregates matrix results into single job for branch protection
rules, you will see the purpose of this once you make a Pull Request and wait
for the checks to complete.

**Steps**:

1. **Aggregate Matrix Results**
   - Echoes aggregation message
   - Provides single job status for GitHub branch protection

**Why aggregate?** GitHub branch protection can require this single job instead
of tracking all matrix combinations and the protection job individually.

## Environment Variables

- **PYTHONDONTWRITEBYTECODE**: `1` (prevents `.pyc` files)
- **UV_NO_SYNC**: `1` (prevents automatic sync on uv commands)

## Required Secrets

- **REPO_TOKEN**: Fine-grained PAT with administration, contents, pages
  permissions
- **CODECOV_TOKEN**: Codecov upload token (recommended, required for private
  repos)
  - See
    [Getting Started - Codecov setup](../../more/getting-started.md#accounts--tokens)
    for details

## Usage

### Automatic Creation

```bash
uv run pyrig mkroot
```

### Manual Trigger

GitHub Actions tab → Health Check → Run workflow

## Best Practices

1. **Fix failures immediately**: Health check blocks the entire pipeline
2. **Monitor coverage**: Maintain 90% minimum coverage
3. **Check all matrix jobs**: Don't ignore platform-specific failures
4. **Update dependencies regularly**: Scheduled runs catch breaking changes
   early
