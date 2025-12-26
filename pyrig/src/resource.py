"""Resource file access utilities for development and PyInstaller builds.

This module provides utilities for accessing static resource files (images,
configuration files, data files, etc.) in a way that works both during
development and when the application is bundled with PyInstaller.

The module uses Python's `importlib.resources` API to provide unified access
to resource files regardless of the execution environment:

    - **Development**: Resources are accessed directly from the filesystem
    - **PyInstaller bundle**: Resources are extracted from the frozen executable
      to a temporary directory (_MEIPASS) and accessed from there

Resources should be placed in `pkg/resources/` directories within your package
structure and accessed via the `get_resource_path` function.

Example:
    >>> import my_project.resources as resources
    >>> from pyrig.src.resource import get_resource_path
    >>> config_path = get_resource_path("config.json", resources)
    >>> data = config_path.read_text()

See Also:
    pyrig.resources: Pyrig's own resource files
    pyrig.dev.utils.resources: Decorators for network fallback to resources
    pyrig.dev.configs.python.resources_init: Generator for project resources package
"""

from importlib.resources import as_file, files
from pathlib import Path
from types import ModuleType


def get_resource_path(name: str, package: ModuleType) -> Path:
    """Get the filesystem path to a resource file.

    Resolves the path to a resource file within a package, handling both
    development (source) and production (PyInstaller bundle) environments.
    Uses `importlib.resources.as_file()` to ensure compatibility with frozen
    executables and zip-imported packages.

    The function uses a context manager internally but returns the path directly.
    The path remains valid for the lifetime of the process because the context
    manager's cleanup is deferred until process exit.

    Args:
        name: The filename of the resource including extension
            (e.g., "icon.png", "config.json", "template.html").
        package: The package module containing the resource. This should be
            the `resources` package itself (e.g., `myapp.resources`), not a
            parent package (e.g., `myapp`).

    Returns:
        A Path object pointing to the resource file. The behavior depends on
        the execution environment:
            - **Development**: Returns the actual file path in the source tree
              (e.g., `/path/to/myapp/resources/icon.png`)
            - **PyInstaller**: Returns a path to the extracted file in the
              temporary directory (e.g., `/tmp/_MEIxxxxxx/myapp/resources/icon.png`)

    Example:
        Basic usage::

            >>> import my_app.resources as resources
            >>> icon_path = get_resource_path("icon.png", resources)
            >>> print(icon_path)
            /path/to/my_app/resources/icon.png

        Accessing resources from subpackages::

            >>> from my_app.resources import data  # subpackage
            >>> csv_path = get_resource_path("users.csv", data)
            >>> import pandas as pd
            >>> df = pd.read_csv(csv_path)

        Accessing resources from dependencies::

            >>> from pyrig import resources as pyrig_resources
            >>> gitignore_path = get_resource_path("GITIGNORE", pyrig_resources)
            >>> content = gitignore_path.read_text()

    Note:
        The returned path is valid for the lifetime of the current process.
        For PyInstaller bundles, the file is extracted to a temporary directory
        that is automatically cleaned up when the process exits.

        The function uses `importlib.resources.as_file()` which handles the
        extraction and cleanup automatically. You don't need to manage the
        context yourself.

    See Also:
        pyrig.dev.utils.resources.return_resource_file_content_on_exceptions:
            Decorator for network fallback to resource files
        pyrig.resources: Pyrig's resource files
    """
    resource_path = files(package) / name
    with as_file(resource_path) as path:
        return path
