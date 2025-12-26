"""pyrig - A Python toolkit to rig up your project.

This package provides an opinionated Python project toolkit that eliminates
setup time and enforces best practices. It standardizes and automates project
setup, configuration, and development workflows.

The package is organized into three main subpackages:

- **pyrig.src**: Runtime utilities for Python introspection, CLI support, Git
  operations, string manipulation, and testing. Safe to use in production code
  with minimal dependencies.

- **pyrig.dev**: Development tools including configuration file generators,
  artifact builders, CLI commands, and testing infrastructure. Only imported
  when executing development commands.

- **pyrig.resources**: Static resource files (templates, licenses, etc.) used
  by development tools for project initialization.

Entry Points:
    The main CLI entry point is `pyrig.dev.cli.cli:main`, registered as the
    `pyrig` console script in pyproject.toml.

Example:
    Initialize a new project::

        $ uv run pyrig init

    Create project structure::

        $ uv run pyrig mkroot

    Generate test skeletons::

        $ uv run pyrig mktests

See Also:
    - pyrig.src: Runtime utilities
    - pyrig.dev: Development tools
    - pyrig.dev.cli: CLI system
    - pyrig.dev.configs: Configuration file generators
"""
