"""Utilities for extracting the invoking project and package names from sys.argv.

Pyrig uses these utilities to support context-aware CLI behavior: shared commands
can inspect which project's entry point was used to invoke them, allowing a single
command implementation to adapt its behavior to the calling project.
"""

import sys
from pathlib import Path

from pyrig.core.strings import kebab_to_snake_case


def project_name_from_argv() -> str:
    """Extract the invoking project name from the command-line entry point.

    Reads ``sys.argv[0]`` and returns its basename. When a project is invoked
    through a registered console-script entry point (e.g. ``uv run my-project``),
    ``sys.argv[0]`` is the path to that entry point script, so its basename is
    the project name as it was registered.

    Returns:
        The basename of ``sys.argv[0]``, which is the project name as registered
        in the console-scripts entry point.

    Example:
        >>> # When invoked as: uv run my-project build
        >>> project_name_from_argv()
        'my-project'
    """
    return Path(sys.argv[0]).name


def package_name_from_argv() -> str:
    """Extract the invoking Python package name from the command-line entry point.

    Converts the project name from ``project_name_from_argv`` into a valid
    Python identifier by replacing hyphens with underscores. This produces the
    importable package name that corresponds to the invoked project, which is
    used to locate that project's CLI modules (e.g. subcommands) at runtime.

    Returns:
        The Python package name corresponding to the invoked project, with
        hyphens replaced by underscores.

    Example:
        >>> # When invoked as: uv run my-project build
        >>> package_name_from_argv()
        'my_project'
    """
    project_name = project_name_from_argv()
    return kebab_to_snake_case(project_name)
