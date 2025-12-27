"""Resource file access utilities for development and PyInstaller builds.

Provides unified access to static resource files using `importlib.resources`, working
in both development and PyInstaller-bundled environments.
"""

from importlib.resources import as_file, files
from pathlib import Path
from types import ModuleType


def get_resource_path(name: str, package: ModuleType) -> Path:
    """Get the filesystem path to a resource file.

    Works in both development and PyInstaller environments using `importlib.resources`.

    Args:
        name: Resource filename (e.g., "icon.png", "config.json").
        package: Package module containing the resource (e.g., `myapp.resources`).

    Returns:
        Path to the resource file (valid for process lifetime).

    Note:
        In PyInstaller bundles, files are extracted to a temporary directory.
    """
    resource_path = files(package) / name
    with as_file(resource_path) as path:
        return path
