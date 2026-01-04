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
        Path to resource file.

        **Important:** For regular file-based packages, this points to the actual
        file. For zip-imported packages or certain PyInstaller configurations,
        this points to a temporary extraction that may be cleaned up when the
        context manager exits. Use the returned path immediately or copy the
        file contents if persistence is needed.

    Note:
        This function uses `as_file` context manager but returns immediately,
        which works correctly for regular files but may cause issues with
        zip-imported packages.
    """
    resource_path = files(package) / name
    with as_file(resource_path) as path:
        return path
