"""CLI utilities for extracting project and package names from command-line arguments.

Provides context-aware CLI behavior by determining which project is being invoked
from `sys.argv[0]`. This is the foundation for pyrig's dynamic command discovery
system, allowing shared commands to adapt behavior based on the invoking project.

These utilities are used internally by pyrig's CLI infrastructure
(``pyrig.dev.cli.cli``) and are available for shared commands that need to know
which project invoked them.

Example:
    A shared ``version`` command that displays the invoking project's version::

        from pyrig.src.cli import get_project_name_from_argv
        from importlib.metadata import version as get_version

        def version() -> None:
            project_name = get_project_name_from_argv()
            print(f"{project_name} version {get_version(project_name)}")
"""

import sys
from pathlib import Path

from pyrig.src.modules.package import get_pkg_name_from_project_name


def get_project_name_from_argv() -> str:
    """Extract the project name from the command-line invocation.

    Extracts the basename of `sys.argv[0]`, which contains the console script
    entry point name when invoked via a registered CLI command. This enables
    shared commands to behave differently based on which project invoked them.

    Returns:
        Project name extracted from the console script entry point.
        For ``uv run my-project cmd``, returns ``"my-project"``.

    Example:
        >>> # When invoked as: uv run my-project build
        >>> get_project_name_from_argv()
        'my-project'

    See Also:
        get_pkg_name_from_argv: Converts the result to a Python package name.
    """
    return Path(sys.argv[0]).name


def get_pkg_name_from_argv() -> str:
    """Extract the Python package name from the command-line invocation.

    Combines `get_project_name_from_argv` with hyphen-to-underscore conversion
    to produce a valid Python package name. This is used by pyrig's CLI command
    discovery to locate the invoking package's modules (e.g., subcommands).

    Returns:
        Python package name corresponding to the invoked project.
        For ``uv run my-project cmd``, returns ``"my_project"``.

    Example:
        >>> # When invoked as: uv run my-project build
        >>> get_pkg_name_from_argv()
        'my_project'

    See Also:
        get_project_name_from_argv: Returns the raw project name without conversion.
        pyrig.src.modules.package.get_pkg_name_from_project_name: conversion function.
    """
    project_name = get_project_name_from_argv()
    return get_pkg_name_from_project_name(project_name)
