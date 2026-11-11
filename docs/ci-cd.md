# CI/CD Pipeline

pyrig generates and manages a complete three-stage GitHub Actions pipeline.
The workflows are produced as `ConfigFile` subclasses, so they are kept correct
automatically by the `pyrig sync` pre-commit hook, just like any other managed file.

---

## Pipeline Overview

`release.yml` is the only workflow triggered by a push to the default branch.
It calls the health check and deploy workflows as **reusable workflows**
(`workflow_call`), running them as jobs in sequence:

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

`Health Check` is also independently triggered by manual dispatch, every pull
request, and a nightly schedule, so it supports on-demand diagnostics while
doubling as both a PR gate and a reusable job called from `release.yml`.
`Deploy` only runs via `workflow_call`, invoked by `release.yml`'s `deploy` job
after `publish` succeeds; since jobs run in dependency order (`needs:`), no
`if` guard is required — `deploy` never executes unless `publish` (and,
transitively, `health-check`) succeeded.
Deploy also calls `repository.yml` and `documentation.yml` as nested
reusable workflows.

---

## Stage 1 — Health Check

**File:** `.github/workflows/health-check.yml`

This workflow executes tests and other general health checks. It has four
triggers: manual dispatch, every pull request, a nightly schedule, and
`workflow_call` (so `release.yml` can run it as a job). Manual dispatch is
useful for on-demand diagnostics; as a PR gate it blocks merging until it
passes; as a nightly job it catches regressions from automatic dependency
upgrades (see below); and as a reusable workflow it acts as the first job in
the release pipeline, gating `publish`.

---

## Stage 2 — Release

**File:** `.github/workflows/release.yml`

**Trigger:** `push` to the default branch.

Three jobs run in dependency order:

- **`health-check`** — calls `health-check.yml` as a reusable workflow.
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

Two core jobs run in this final stage:

- **`repository`** — calls `repository.yml` as a reusable workflow to apply
  repository settings and protection rulesets via the GitHub API. The call
  forwards `REPO_TOKEN` and grants `contents: read`.
- **`documentation`** — calls `documentation.yml` as a reusable workflow to
  build and deploy the site. The call forwards `REPO_TOKEN` and grants
  `contents: read`, `pages: write`, and `id-token: write`.

### Repository configuration

**File:** `.github/workflows/repository.yml`

**Trigger:** `workflow_call` only, invoked by the deploy workflow.

The `configure` job checks out the repository, then runs
`.github/configure.sh` using `.github/settings.json`. It uses the `repository`
environment and `contents: read` for checkout. The script authenticates to
the GitHub API separately using `REPO_TOKEN`, which is forwarded from release
through deploy to the repository workflow.

### Documentation deployment

**File:** `.github/workflows/documentation.yml`

**Trigger:** `workflow_call` only, invoked by the deploy workflow.

The `build` job checks out the project, builds the site, and uploads a Pages
artifact with `contents: read`. The `deploy` job runs only after `build`
succeeds, enables GitHub Pages using `REPO_TOKEN`, and deploys the artifact.
It uses the `documentation` environment and requires `pages: write` and
`id-token: write`. Release and deploy forward the secret and permissions to
the nested workflow.

!!! warning "Important"
    If your repository is private, the published docs site is still publicly accessible.
    Please check how to [change the visibility of your GitHub Pages site](https://docs.github.com/en/enterprise-cloud@latest/pages/getting-started-with-github-pages/changing-the-visibility-of-your-github-pages-site)
    in the repository settings. Pyrig does not do this for you as it is not
    free for private repositories.

!!! tip
    Keep your documentation public for users and only document user facing
    relevant information and avoid exposing internal implementation details.

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

All workflow files are managed `ConfigFile` instances, so they can be
extended or overridden in the same way as any other managed file in pyrig.
Run `pyrig mk subcls` and search for the workflow class you want to change to
generate a correctly placed subclass skeleton.
Override the methods that need changing — jobs, triggers, steps, permissions,
or environment variables. The `WorkflowConfigFile` base class provides
composable helpers for common patterns (matrix strategies, step builders,
trigger constructors) so custom workflows stay concise and consistent with
the generated ones.

Run `pyrig sync` after any change to update or regenerate the workflow files.
