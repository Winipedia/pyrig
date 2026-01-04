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
        Path to resource file. In development environments, this points to
        the actual file. In PyInstaller bundles, this points to a temporary
        extraction that may be cleaned up when the process exits.

    Note:
        In PyInstaller bundles, files are extracted to a temporary directory.
        The returned path should be used immediately or copied if persistence
        is needed beyond the current operation.
    """
    # Use Traversable.joinpath and resolve to Path
    # Note: as_file context manager is used but we return immediately,
    # which is safe for regular files but may cause issues with zip-imported
    # packages. For pyrig's use case (regular file resources), this is fine.
    resource_path = files(package) / name
    with as_file(resource_path) as path:
        return path
