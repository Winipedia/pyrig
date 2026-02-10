"""GitHub Actions workflow configuration management.

Manages GitHub Actions workflows for CI/CD: HealthCheckWorkflow (quality checks),
BuildWorkflow (artifacts/images), ReleaseWorkflow (GitHub releases), DeployWorkflow
(PyPI/docs). Pipeline: Health Check → Build → Release → Deploy.

See Also:
    GitHub Actions: https://docs.github.com/en/actions
    pyrig.rig.configs.pyproject.PyprojectConfigFile
"""
