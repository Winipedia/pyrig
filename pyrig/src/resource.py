"""Resource file access utilities for development and PyInstaller builds.

This module provides utilities for accessing static resource files (images,
configuration files, data files, etc.) in a way that works both during
development and when the application is bundled with PyInstaller.

When running from source, resources are accessed from the filesystem. When
running from a PyInstaller bundle, resources are extracted from the frozen
executable's temporary directory (MEIPASS). Using `importlib.resources`
handles both cases transparently.

Resources should be placed in `pkg/dev/artifacts/resources/` directories
and accessed via the `get_resource_path` function.

Example:
    >>> import my_project.dev.artifacts.resources as resources
    >>> from pyrig.src.resource import get_resource_path
    >>> config_path = get_resource_path("config.json", resources)
    >>> data = config_path.read_text()
"""

from importlib.resources import as_file, files
from pathlib import Path
from types import ModuleType


def get_resource_path(name: str, package: ModuleType) -> Path:
    """Get the filesystem path to a resource file.

    Resolves the path to a resource file within a package, handling both
    development (source) and production (PyInstaller bundle) environments.
    Uses `importlib.resources` to ensure compatibility with frozen executables.

    Args:
        name: The filename of the resource including extension
            (e.g., "icon.png", "config.json").
        package: The package module containing the resource. This should be
            the `resources` package itself, not a parent package.

    Returns:
        A Path object pointing to the resource file. In development, this
        is the actual file path. In a PyInstaller bundle, this is a path
        to the extracted file in the temporary directory.

    Example:
        >>> import my_app.dev.artifacts.resources as resources
        >>> icon_path = get_resource_path("icon.png", resources)
        >>> print(icon_path)
        /path/to/my_app/dev/artifacts/resources/icon.png

    Note:
        The returned path is only valid within the context of the current
        process. For PyInstaller bundles, the file is extracted to a
        temporary directory that is cleaned up when the process exits.
    """
    resource_path = files(package) / name
    with as_file(resource_path) as path:
        return path
