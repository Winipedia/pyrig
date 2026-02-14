"""Development-time infrastructure for pyrig projects.

Provides development tools, configuration management, CLI commands, artifact builders,
and testing infrastructure.

Subpackages:
    builders: Artifact building (PyInstaller executables, distributions)
    cli: Command-line interface and subcommands
    configs: Configuration file generators and managers
    tools: Tool wrappers (uv, git, ruff, pytest, etc.)
    tests: Testing infrastructure and pytest fixtures
    utils: Development utilities and helpers

Note:
    Development dependencies only. Not for production runtime code.
"""
