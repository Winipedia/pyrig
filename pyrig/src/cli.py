"""Command-line interface utilities for project and package name extraction.

This module provides utilities for extracting project and package names from
command-line arguments. These functions enable context-aware CLI behavior by
determining which project is being invoked, allowing shared commands to adapt
to the calling project.

The utilities are primarily used by pyrig's dynamic command discovery system
to determine which project's commands should be loaded and executed.

Example:
    >>> # When running: uv run myproject version
    >>> from pyrig.src.cli import get_project_name_from_argv, get_pkg_name_from_argv
    >>> get_project_name_from_argv()
    'myproject'
    >>> get_pkg_name_from_argv()
    'myproject'  # or 'my_project' if project name is 'my-project'
"""

import sys
from pathlib import Path

from pyrig.src.modules.package import get_pkg_name_from_project_name


def get_project_name_from_argv() -> str:
    """Extract the project name from the command-line invocation.

    Parses `sys.argv[0]` to determine which project is being invoked. This
    enables shared CLI commands to adapt their behavior based on the calling
    project.

    The function extracts the base name from `sys.argv[0]`, which typically
    contains the script name or entry point name (e.g., "pyrig", "myproject").

    Returns:
        The project name extracted from `sys.argv[0]`. This is the name used
        in the console script entry point (e.g., "pyrig" for pyrig, "myproject"
        for a project named myproject).

    Example:
        >>> # When running: uv run pyrig version
        >>> get_project_name_from_argv()
        'pyrig'

        >>> # When running: uv run my-project status
        >>> get_project_name_from_argv()
        'my-project'

    Note:
        This function is used by the CLI discovery system to determine which
        project's commands should be loaded. It enables the same shared command
        to behave differently depending on which project invokes it.

    See Also:
        get_pkg_name_from_argv: Get the Python package name from argv
        pyrig.dev.cli.cli.add_subcommands: Uses this to discover project commands
    """
    return Path(sys.argv[0]).name


def get_pkg_name_from_argv() -> str:
    """Extract the Python package name from the command-line invocation.

    Combines `get_project_name_from_argv()` with project-to-package name
    conversion to determine the Python package name. This is useful when you
    need to import modules from the calling project.

    The conversion follows Python package naming conventions: hyphens in the
    project name are replaced with underscores for the package name.

    Returns:
        The Python package name corresponding to the project being invoked.
        Hyphens in the project name are converted to underscores.

    Example:
        >>> # When running: uv run pyrig version
        >>> get_pkg_name_from_argv()
        'pyrig'

        >>> # When running: uv run my-project status
        >>> get_pkg_name_from_argv()
        'my_project'

    Note:
        This function is used by the CLI discovery system to dynamically import
        the correct project's modules (e.g., `{package}.dev.cli.subcommands`).

    See Also:
        get_project_name_from_argv: Get the project name from argv
        pyrig.src.modules.package.get_pkg_name_from_project_name: Conversion logic
        pyrig.dev.cli.cli.add_subcommands: Uses this to import project modules
    """
    project_name = get_project_name_from_argv()
    return get_pkg_name_from_project_name(project_name)
