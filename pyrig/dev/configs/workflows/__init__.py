"""GitHub Actions workflow configuration management.

This subpackage provides configuration file managers for GitHub Actions workflow
files that automate CI/CD processes for Python projects.

The subpackage includes four main workflows:
    - **HealthCheckWorkflow**: Runs on PRs, pushes, and scheduled intervals to
      verify code quality (linting, type checking, security, tests)
    - **BuildWorkflow**: Triggers after health checks pass on main branch to
      build artifacts and container images
    - **ReleaseWorkflow**: Triggers after builds complete to create GitHub
      releases with tags and changelogs
    - **PublishWorkflow**: Triggers after releases to publish packages to PyPI
      and documentation to GitHub Pages

Workflow Pipeline:
    1. Health Check (on PR/push/schedule) → runs tests and quality checks
    2. Build (on main after health check) → builds artifacts and images
    3. Release (after build) → creates GitHub release with tags
    4. Publish (after release) → publishes to PyPI and GitHub Pages

All workflows use:
    - OS matrix (Ubuntu, macOS, Windows)
    - Python version matrix (supported versions from pyproject.toml)
    - uv package manager for fast dependency installation
    - Caching for dependencies and build artifacts

Modules:
    health_check: CI workflow for code quality and tests
    build: Artifact and container image building
    release: GitHub release creation with tags
    publish: PyPI and documentation publishing
    base: Base workflow classes and utilities

See Also:
    GitHub Actions: https://docs.github.com/en/actions
    pyrig.dev.configs.pyproject.PyprojectConfigFile
        Used to determine Python versions and project metadata
"""
