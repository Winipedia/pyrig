"""CLI utilities for extracting project and package names from command-line arguments.

Enables context-aware CLI behavior by determining which project is being invoked.
"""

import sys
from pathlib import Path

from pyrig.src.modules.package import get_pkg_name_from_project_name


def get_project_name_from_argv() -> str:
    """Extract the project name from the command-line invocation.

    Parses `sys.argv[0]` to determine which project is being invoked.

    Returns:
        Project name from the console script entry point.
    """
    return Path(sys.argv[0]).name


def get_pkg_name_from_argv() -> str:
    """Extract the Python package name from the command-line invocation.

    Converts the project name to a Python package name (hyphens → underscores).

    Returns:
        Python package name corresponding to the invoked project.
    """
    project_name = get_project_name_from_argv()
    return get_pkg_name_from_project_name(project_name)
