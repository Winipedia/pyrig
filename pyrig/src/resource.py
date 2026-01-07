"""Resource file access utilities for development and PyInstaller builds.

Provides unified access to static resource files using `importlib.resources`, working
in both development and PyInstaller-bundled environments. The primary function
`get_resource_path` abstracts away environment-specific path resolution.
"""

from importlib.resources import as_file, files
from pathlib import Path
from types import ModuleType


def get_resource_path(name: str, package: ModuleType) -> Path:
    """Get filesystem path to a resource file within a package.

    Provides cross-platform, environment-agnostic access to static resources bundled
    with Python packages. Works seamlessly in development (file-based packages) and
    PyInstaller executables (extracted to temporary directories).

    Args:
        name: Resource filename (e.g., "config.json", "icon.png"). Can include
            subdirectory paths relative to the package (e.g., "templates/email.html").
        package: Package module object containing the resource. Import the package's
            `__init__.py` module and pass it directly.

    Returns:
        Absolute path to the resource file.

    Raises:
        TypeError: If package is not a valid module object.
        FileNotFoundError: If the resource file does not exist in the package.

    Example:
        >>> from myapp import resources
        >>> config_path = get_resource_path("config.json", resources)
        >>> config_data = config_path.read_text()

    Warning:
        For file-based packages (typical development and PyInstaller builds), the
        returned path points to the actual file. For zip-imported packages, the path
        may point to a temporary extraction. Use the path immediately or copy contents
        if persistence beyond the current call is needed.

    Note:
        This function exits the `as_file` context manager before returning, which
        works reliably for file-based packages but may cause path invalidation for
        zip-imported packages. This is acceptable for pyrig's use cases where
        packages are always file-based.
    """
    resource_path = files(package) / name
    with as_file(resource_path) as path:
        return path
