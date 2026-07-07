# CI/CD Pipeline

pyrig generates and manages a complete three-stage GitHub Actions pipeline.
The workflows are produced as `ConfigFile` subclasses, so they are kept correct
automatically by the `pyrig sync` pre-commit hook, just like any other managed file.

---

## Pipeline Overview

The three workflows form a chain where each stage triggers the next on completion:

```text
Pull Request / Push / Schedule / Manual
            │
            ▼
    ┌─────────────────┐
    │  Health Check   │  ← the only gate for merging PRs
    └────────┬────────┘
             │ completes on default branch (push-triggered only)
             ▼
    ┌─────────────────┐
    │    Release      │  ← tags and publishes a GitHub Release
    └────────┬────────┘
             │ completes
             ▼
    ┌─────────────────┐
    │     Deploy      │  ← deploys documentation to GitHub Pages
    └─────────────────┘
```

All transitions use `workflow_run: completed` triggers, meaning a stage only
fires when the previous stage finishes. Each downstream stage also guards its
jobs with an `if` condition that checks the triggering run succeeded, so a
failure anywhere in the chain stops propagation cleanly.

---

## Stage 1 — Health Check

**File:** `.github/workflows/health_check.yml`

This workflow executes tests and other general health checks on every push to
`main`, every pull request, and on a nightly schedule. It is a gate for
merging PRs, since it runs on every PR and blocks merging until it passes.

---

## Stage 2 — Release

**File:** `.github/workflows/release.yml`

**Trigger:** `Health Check` workflow completes on the default branch.

The **`publish`** job only runs when the triggering health check both succeeded
and was itself triggered by a push to the default branch. Scheduled runs,
manual dispatches, and pull request runs never produce a release.
Before tagging, it applies repository settings and branch protection rulesets
via the GitHub API. Then it tags the current commit, pushes the tag, generates
a changelog, and creates a GitHub Release.
Important: The release workflow creates a new tag, which will fail if that tag
already exists. This means you must ensure the version is updated in `pyproject.toml`
before pushing to the default branch, otherwise the release workflow will
fail on the existing tag. This is a common source of confusion, so make sure
to update the version in `pyproject.toml` before creating a new release.
This is easily done by running `uv version --bump patch` (or `minor`/`major`).

---

## Stage 3 — Deploy

**File:** `.github/workflows/deploy.yml`

**Trigger:** `Release` workflow completes.

One job runs in this final stage, gated on the triggering release having
succeeded:

- **`documentation`** — builds the MkDocs documentation site and
  deploys it to GitHub Pages. This job requires `pages: write` and
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

## Customising the Pipeline

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
