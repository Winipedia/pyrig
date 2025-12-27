"""GitHub Actions workflow configuration management.

Manages GitHub Actions workflows for CI/CD: HealthCheckWorkflow (quality checks),
BuildWorkflow (artifacts/images), ReleaseWorkflow (GitHub releases), PublishWorkflow
(PyPI/docs). Pipeline: Health Check → Build → Release → Publish.

See Also:
    GitHub Actions: https://docs.github.com/en/actions
    pyrig.dev.configs.pyproject.PyprojectConfigFile
"""
