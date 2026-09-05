# CI/CD Pipeline

pyrig generates and manages a complete three-stage GitHub Actions pipeline.
The workflows are produced as `ConfigFile` subclasses, so they are kept correct
automatically by the `pyrig sync` pre-commit hook, just like any other managed file.

---

## Pipeline Overview

`release.yml` is the only workflow triggered by a push to the default branch.
It calls the other two workflows as **reusable workflows** (`workflow_call`),
running them as jobs in sequence:

```text
                Push to default branch
                        │
                        ▼
              ┌───────────────────┐
              │     Release       │
              │                   │
              │  ┌─────────────┐  │
              │  │Health Check │  │  ← called via workflow_call
              │  └──────┬──────┘  │
              │         ▼         │
              │  ┌─────────────┐  │
              │  │   Publish   │  │  ← tags and publishes a GitHub Release
              │  └──────┬──────┘  │
              │         ▼         │
              │  ┌─────────────┐  │
              │  │   Deploy    │  │  ← called via workflow_call
              │  └─────────────┘  │
              └───────────────────┘
```

`Health Check` is also independently triggered by every pull request and a
nightly schedule, so it doubles as both a PR gate and a reusable job called
from `release.yml`. `Deploy` only runs via `workflow_call`, invoked by
`release.yml`'s `deploy` job after `publish` succeeds; since jobs run in
dependency order (`needs:`), no `if` guard is required — `deploy` never
executes unless `publish` (and, transitively, `health-check`) succeeded.

Every job in the deploy workflow gets its own GitHub Actions environment,
named after the job's stable ID automatically.

---

## Stage 1 — Health Check

**File:** `.github/workflows/health_check.yml`

This workflow executes tests and other general health checks. It has three
triggers: every pull request, a nightly schedule, and `workflow_call` (so
`release.yml` can run it as a job). As a PR gate it blocks merging until it
passes; as a nightly job it catches regressions from automatic dependency
upgrades (see below); as a reusable workflow it acts as the first job in the
release pipeline, gating `publish`.

---

## Stage 2 — Release

**File:** `.github/workflows/release.yml`

**Trigger:** `push` to the default branch.

Three jobs run in dependency order:

- **`health-check`** — calls `health_check.yml` as a reusable workflow.
- **`publish`** — runs only if `health-check` succeeds (`needs:`). Creates a
  GitHub Release with auto-generated release notes, tagging the current
  commit in the same call.
- **`deploy`** — runs only if `publish` succeeds (`needs:`). Calls
  `deploy.yml` as a reusable workflow.

!!! warning "Important"
    The release workflow creates a new tag, which will fail if that tag
    already exists. This means you must ensure the version is updated in
    `pyproject.toml` before pushing to the default branch, otherwise the
    release workflow will fail on the existing tag. This is a common source
    of confusion, so make sure to update the version in `pyproject.toml`
    before creating a new release. This is easily done by running
    `uv version --bump patch` (or `minor`/`major`).

---

## Stage 3 — Deploy

**File:** `.github/workflows/deploy.yml`

**Trigger:** `workflow_call` only, invoked by `release.yml`'s `deploy` job.

Two jobs run in this final stage:

- **`repository`** — applies repository settings and protection rulesets,
  and enables GitHub's private vulnerability reporting, all via the GitHub
  API. Requires `contents: read` at the job level; the configuration step
  itself authenticates separately via the `REPO_TOKEN` secret.
- **`documentation`** — builds the documentation site and deploys it to
  GitHub Pages. This job requires `contents: read`, `pages: write`, and
  `id-token: write` permissions at the job level.

---

## Automatic Dependency Updates Checks

A notable property of the pipeline is that **dependency
upgrades happen inside CI** in the health check stage. It runs `uv lock --upgrade`
to pull the latest dependency versions within declared constraints. This ensures
your project catches problems caused by new versions in the dependencies early.
This way the regular nightly health check runs will catch any issues caused by
dependency upgrades automatically.
If you need specific versions of packages you need to pin them in `pyproject.toml`
to prevent it from being updated by the pipeline.

---

## Customizing the Pipeline

All three workflow files are managed `ConfigFile` instances, so they can be
extended or overridden in the same way as any other managed file in pyrig.
Run `pyrig mk subcls` and search for the workflow class you want to change
(`HealthCheckWorkflowConfigFile`, `ReleaseWorkflowConfigFile`, or
`DeployWorkflowConfigFile`) to generate a correctly placed subclass skeleton.
Override the methods that need changing — jobs, triggers, steps, permissions,
or environment variables. The `WorkflowConfigFile` base class provides
composable helpers for common patterns (matrix strategies, step builders,
trigger constructors) so custom workflows stay concise and consistent with
the generated ones.

Run `pyrig sync` after any change to update or regenerate the workflow files.
