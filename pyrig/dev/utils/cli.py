"""CLI utilities."""

import sys
from pathlib import Path

from pyrig.src.modules.package import get_pkg_name_from_project_name


def get_project_name_from_argv() -> str:
    """Get the project name."""
    return Path(sys.argv[0]).name


def get_pkg_name_from_argv() -> str:
    """Get the project and package name."""
    project_name = get_project_name_from_argv()
    return get_pkg_name_from_project_name(project_name)
