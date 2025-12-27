"""Resource file access utilities for development and PyInstaller builds.

Provides unified access to static resource files using `importlib.resources`, working
in both development and PyInstaller-bundled environments.
"""

from importlib.resources import as_file, files
from pathlib import Path
from types import ModuleType


def get_resource_path(name: str, package: ModuleType) -> Path:
    """Get filesystem path to resource file.

    Works in development and PyInstaller environments.

    Args:
        name: Resource filename.
        package: Package module containing resource.

    Returns:
        Path to resource file (valid for process lifetime).

    Note:
        In PyInstaller bundles, files extracted to temporary directory.
    """
    resource_path = files(package) / name
    with as_file(resource_path) as path:
        return path
