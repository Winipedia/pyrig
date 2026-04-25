"""Utilities for accessing resource files bundled with Python packages.

Provides environment-agnostic path resolution and content reading for static
resources, supporting both regular file-based packages and PyInstaller-bundled
executables.
"""

from importlib.resources import as_file, files
from pathlib import Path
from types import ModuleType

from pyrig.core.strings import read_text_utf8


def resource_content(resource_name: str, package: ModuleType) -> str:
    """Read the contents of a resource file as a UTF-8 string.

    Args:
        resource_name: Filename of the resource (e.g., ``"config.json"``).
        package: Package module containing the resource.

    Returns:
        File contents decoded as a UTF-8 string.
    """
    path = resource_path(resource_name, package)
    return read_text_utf8(path)


def resource_path(name: str, package: ModuleType) -> Path:
    """Resolve the filesystem path of a resource file bundled with a package.

    Uses ``importlib.resources`` to locate resource files in a way that works in
    both development (file-based packages) and PyInstaller executable environments,
    where resources may be extracted to a temporary directory before use.

    Args:
        name: Filename of the resource (e.g., ``"config.json"``). May include a
            subdirectory path relative to the package root
            (e.g., ``"templates/email.html"``).
        package: Package module containing the resource.

    Returns:
        Absolute path to the resource file.

    Raises:
        TypeError: If ``package`` is not a valid module object.

    Note:
        The path is resolved from within an ``as_file`` context manager. For
        file-based packages (standard in development and PyInstaller builds), the
        path points to the actual file and remains valid after this function
        returns. For zip-imported packages, the temporary extraction may be cleaned
        up once the context exits — though pyrig packages are always file-based, so
        this is not a concern in practice.

        The returned path is not validated for existence. Accessing a missing
        resource will raise ``FileNotFoundError``.
    """
    resource_path = files(package) / name
    with as_file(resource_path) as path:
        return path
