# CI/CD Pipeline

pyrig generates and manages a complete four-stage GitHub Actions pipeline.
The workflows are produced as `ConfigFile` subclasses, so they are kept correct
automatically by `pyrig mkroot` and validated on every test run just like any other
managed file.

---

## Pipeline Overview

The four workflows form a chain where each stage triggers the next on completion:

```text
Pull Request / Push / Schedule / Manual
            │
            ▼
    ┌─────────────────┐
    │  Health Check   │  ← the only gate for merging PRs
    └────────┬────────┘
             │ completes on default branch (non-scheduled only)
             ▼
    ┌─────────────────┐
    │     Build       │  ← produces distributable artifacts
    └────────┬────────┘
             │ completes
             ▼
    ┌─────────────────┐
    │    Release      │  ← tags and publishes a GitHub Release
    └────────┬────────┘
             │ completes
             ▼
    ┌─────────────────┐
    │     Deploy      │  ← publishes to PyPI + GitHub Pages
    └─────────────────┘
```

All transitions use `workflow_run: completed` triggers, meaning a stage only
fires when the previous stage finishes. Each downstream stage also guards its
jobs with an `if` condition that checks the triggering run succeeded, so a
failure anywhere in the chain stops propagation cleanly.

Build is not triggered by scheduled health checks, since they serve as a continuous
health signal rather than a release signal. Only pushes and PR merges trigger builds.

---

## Stage 1 — Health Check

**File:** `.github/workflows/health_check.yml`

This workflow executes tests and other general health checks on every push to
`main`, every pull request, and on a nightly schedule. It is a gate for
merging PRs, since it runs on every PR and blocks merging until it passes.

---

## Stage 2 — Build

**File:** `.github/workflows/build.yml`

This one build all artifacts on every operating system via a matrix strategy.
It also build a container image on linux using the generated `Containerfile`
and then adds all of these artifacts to the workflow's artifact store,
making them available for the next stage in the pipeline.

---

## Stage 3 — Release

**File:** `.github/workflows/release.yml`

**Trigger:** `build` workflow completes.

The release job runs only when the triggering build succeeded.
It tags the current commit with the version and pushes the tag to the repository.
Then it creates a GitHub Release with the new tag and attaches the build
artifacts from the previous stage.

---

## Stage 4 — Deploy

**File:** `.github/workflows/deploy.yml`

**Trigger:** `release` workflow completes.

Two independent jobs run in this final stage, both gated on the triggering
release having succeeded:

- **`package`** — builds a Python wheel and publishes it to PyPI using
  the `PYPI_TOKEN` secret. The publish step is conditional: if `PYPI_TOKEN` is
  not configured in the repository secrets, the step is skipped rather than
  failing. This makes the workflow safe to run for projects that are not yet
  published to PyPI.

- **`documentation`** — builds the MkDocs documentation site and
  deploys it to GitHub Pages. This job requires `pages: write` and
  `id-token: write` permissions at the job level.

---

## Automatic Version and Dependency Management

A notable property of the pipeline is that **dependency
upgrades happen inside CI** in the health check stage. It runs `uv lock --upgrade`
to pull the latest dependency versions within declared constraints. This ensures your
project catches problems caused by new versions in the dependencies early.
If you need specific versions of packages you need to pin them in `pyproject.toml`
to prevent it from being updated by the pipeline.

---

## Customising the Pipeline

All four workflow files are managed `ConfigFile` instances, so they can be
extended or overridden in the same way as any other managed file in pyrig.
Subclass the relevant workflow class
(`HealthCheckWorkflowConfigFile`, `BuildWorkflowConfigFile`,
`ReleaseWorkflowConfigFile`, `DeployWorkflowConfigFile`) in your project's
`rig/configs/` tree and override the methods that need changing — jobs,
triggers, steps, permissions, or environment variables. The `WorkflowConfigFile`
base class provides composable helpers for all common patterns (matrix
strategies, step builders, trigger constructors) so custom workflows stay
concise and consistent with the generated ones.

Run `pyrig mkroot` after any change to regenerate the workflow files.
