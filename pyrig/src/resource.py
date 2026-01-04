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

    Warning:
        This function returns a path from within a context manager that exits
        immediately after return. For regular file-based packages, this works
        correctly. However, for zip-imported packages or certain PyInstaller
        configurations, the temporary file may be cleaned up. Use the returned
        path immediately or copy the file contents if persistence is needed.
    """
    # Use Traversable.joinpath and resolve to Path
    # Note: as_file context manager is used but we return immediately,
    # which is safe for regular files but may cause issues with zip-imported
    # packages. For pyrig's use case (regular file resources), this is fine.
    resource_path = files(package) / name
    with as_file(resource_path) as path:
        return path
