"""Development-time infrastructure for pyrig projects.

This package provides comprehensive development tools, configuration management,
CLI commands, artifact builders, and testing infrastructure for Python projects
using pyrig. These components are designed for use during development and CI/CD
workflows but are not required at runtime.

The package is organized into several subpackages:

Subpackages:
    builders: Artifact building tools for creating executables and distributions.
        Includes PyInstaller integration for creating standalone executables.

    cli: Command-line interface for pyrig development commands. Provides the
        main CLI entry point and subcommands for project management, testing,
        configuration generation, and more.

    configs: Configuration file generators and managers. Includes generators for
        pyproject.toml, .gitignore, GitHub workflows, Docker containers, testing
        configurations, documentation configs, and more.

    tests: Testing infrastructure and pytest fixtures. Provides shared test
        fixtures, configuration, and utilities for testing pyrig itself and
        projects using pyrig.

    utils: Development utilities and helper functions. Includes package discovery,
        version constraint parsing, resource fallback decorators, git utilities,
        and pytest fixture decorators.

Usage:
    This package is typically accessed through the pyrig CLI::

        $ pyrig --help
        $ pyrig init
        $ pyrig test
        $ pyrig build

    Or by importing specific utilities in development scripts::

        >>> from pyrig.dev.utils.packages import find_packages, get_src_package
        >>> from pyrig.dev.utils.versions import VersionConstraint
        >>> from pyrig.dev.configs.pyproject import PyprojectConfig

Note:
    The components in this package are development dependencies and should not
    be imported or used in production runtime code. They are intended for:

    - Project scaffolding and initialization
    - Configuration file generation and management
    - Development workflow automation
    - Testing and CI/CD pipelines
    - Building and packaging artifacts

See Also:
    pyrig.src: Runtime source code and utilities
    pyrig.resources: Static resource files used by development tools
"""
