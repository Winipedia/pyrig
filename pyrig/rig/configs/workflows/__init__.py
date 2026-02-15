"""GitHub Actions workflow configuration management.

Manages GitHub Actions workflows for CI/CD:
    HealthCheckWorkflowConfigFile (quality checks),
    BuildWorkflowConfigFile (artifacts/images),
    ReleaseWorkflowConfigFile (GitHub releases),
    DeployWorkflowConfigFile (PyPI/docs).
    Pipeline: Health Check → Build → Release → Deploy.

See Also:
    GitHub Actions: https://docs.github.com/en/actions
    pyrig.rig.configs.pyproject.PyprojectConfigFile
"""
