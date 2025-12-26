"""Constants used across pyrig modules.

This module defines constants that are shared across multiple pyrig modules,
primarily related to project configuration and dependency management.

Constants:
    STANDARD_DEV_DEPS: List of development dependencies that are automatically
        added to all pyrig-based projects.
"""

STANDARD_DEV_DEPS: list[str] = ["pyrig-dev"]
"""Standard development dependencies for pyrig-based projects.

This list contains development dependencies that are automatically added to
the `[dependency-groups] dev` section of pyproject.toml for all projects
using pyrig.

The `pyrig-dev` package is a meta-package that includes all development tools
required for pyrig-based projects:
    - Testing: pytest, pytest-cov, pytest-mock
    - Type checking: mypy, type stubs
    - Linting/formatting: ruff
    - Security: bandit
    - Documentation: mkdocs, mkdocs-material, mkdocstrings
    - Building: pyinstaller, pillow
    - Pre-commit: pre-commit
    - Configuration: tomlkit, pyyaml, dotenv
    - Git integration: pygithub
    - And more

By using a meta-package, projects get all necessary development tools with
a single dependency, ensuring consistency across all pyrig-based projects.

Note:
    This constant is used by PyprojectConfigFile to automatically add
    development dependencies during project initialization and configuration
    updates.

See Also:
    pyrig.dev.configs.pyproject.PyprojectConfigFile.get_standard_dev_dependencies:
        Uses this constant to populate dev dependencies
    pyrig.dev.cli.commands.init_project.adding_dev_dependencies:
        Installs these dependencies during project initialization
"""
