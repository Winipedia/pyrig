# GitHub Actions Workflows

GitHub Actions workflow configuration files for CI/CD automation.

## Overview

Pyrig generates GitHub Actions workflows that automate:
- Continuous integration (linting, type checking, testing)
- Building artifacts (wheels, container images)
- Creating releases (versioning, changelogs, GitHub releases)
- Publishing (PyPI, GitHub Pages documentation)

All workflows are defined in Python using the `Workflow` base class and automatically generated as YAML files in `.github/workflows/`.

## Architecture

See [Workflow Architecture](architecture.md) for details on:
- Workflow base class and declarative API
- Inheritance hierarchy
- Naming conventions
- Opt-out mechanism
- Complete CI/CD pipeline

## Workflow Files

### [health_check.yaml](health_check.md)
Continuous integration workflow that validates code quality and runs tests across OS and Python versions.

### [build.yaml](build.md)
Artifact building workflow that creates platform-specific executables and container images.

### [release.yaml](release.md)
Release creation workflow that versions, tags, and publishes GitHub releases with artifacts.

### [publish.yaml](publish.md)
Publishing workflow that distributes packages to PyPI and documentation to GitHub Pages.

## Quick Start

### Automatic Creation

```bash
uv run pyrig mkroot
```

Creates all four workflows in `.github/workflows/`.

### Required Secrets

Add these to your GitHub repository secrets:

- **REPO_TOKEN**: Fine-grained personal access token with permissions:
  - administration: read, write (needed to protect repo and main branch via pyrig protect-repo in the health_check workflow)
  - contents: read, write (needed to create and push commits and tags in the release workflow)
  - pages: read, write (needed to activate and publish documentation to GitHub Pages in the publish workflow)
- **PYPI_TOKEN**: PyPI API token (for publishing packages)
- **CODECOV_TOKEN**: Codecov token (recommended for all repos, required for private repos)
  - See [Getting Started - Codecov setup](../more/getting-started.md#required-accounts--tokens) for details

### Workflow Pipeline

```
1. Health Check (on PR/push/schedule)
   ↓
2. Build (on health check success, main only)
   ↓
3. Release (on build success)
   ↓
4. Publish (on release success)
```

## Customization

### Opting Out of Workflows

To disable a workflow without deleting it:

1. Edit the workflow Python class
2. Replace all steps with `step_opt_out_of_workflow()`
3. Run `uv run pyrig mkroot`

The workflow will exist but never execute.

### Modifying Workflows

1. Edit the workflow class in `myapp/dev/configs/workflows/`
2. Override methods like `get_jobs()`, `get_workflow_triggers()`, etc.
3. Run `uv run pyrig mkroot` to regenerate YAML

## Best Practices

1. **Don't edit YAML directly**: Always modify Python subclasses of `Workflow`
2. **Test locally first**: Run `uv run pyrig mkroot` before committing
3. **Use matrix strategies**: Test across OS and Python versions
4. **Configure secrets properly**: Workflows fail without required tokens
5. **Monitor workflow runs**: Check GitHub Actions tab for failures

