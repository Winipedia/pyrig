"""Resource file access utilities for development and PyInstaller builds.

Provides unified access to static resource files using `importlib.resources`, working
in both development and PyInstaller-bundled environments. The primary function
`resource_path` abstracts away environment-specific path resolution.
"""

from importlib.resources import as_file, files
from pathlib import Path
from types import ModuleType


def resource_path(name: str, package: ModuleType) -> Path:
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
        Path: Absolute filesystem path to the resource file.

    Raises:
        AttributeError: If package is not a valid module object.
        ModuleNotFoundError: If package string name cannot be found.

    Example:
        >>> from pyrig import resources
        >>> path = resource_path("GITIGNORE", resources)
        >>> content = path.read_text()

    Warning:
        For file-based packages (typical development and PyInstaller builds), the
        returned path points to the actual file and remains valid after the function
        returns. For zip-imported packages, the path may point to a temporary
        extraction that could be cleaned up after the context manager exits, though
        the path is returned while still within the context. Use the path immediately
        or copy contents if persistence is critical.

    Note:
        The returned path is not validated for existence. If the named resource does
        not exist, the caller will encounter `FileNotFoundError` when accessing it.

        The function returns the path from within the `as_file` context manager.
        For file-based packages, the path remains valid. For zip-imported packages,
        this is acceptable for pyrig's use cases where packages are always file-based.
    """
    resource_file = files(package) / name
    with as_file(resource_file) as path:
        return path
