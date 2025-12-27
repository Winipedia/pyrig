"""Development-time infrastructure for pyrig projects.

Provides development tools, configuration management, CLI commands, artifact builders,
and testing infrastructure. For development and CI/CD only, not runtime use.

Subpackages:
    builders: Artifact building (PyInstaller executables, distributions)
    cli: Command-line interface and subcommands
    configs: Configuration file generators and managers
    tests: Testing infrastructure and pytest fixtures
    utils: Development utilities and helpers

Note:
    Development dependencies only. Not for production runtime code.
"""
