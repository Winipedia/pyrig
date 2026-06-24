"""Path resolution and content reading for static files bundled with a package."""

from importlib.resources import files
from pathlib import Path
from types import ModuleType

from pyrig.core.strings import read_text_utf8


def resource_content(name: str, package: ModuleType) -> str:
    """Read a bundled resource file and return its contents as a UTF-8 string.

    Args:
        name: Filename of the resource (e.g., `"config.json"`). May include a
            subdirectory path relative to the package root
            (e.g., `"templates/email.html"`).
        package: Package module that contains the resource.

    Returns:
        File contents as a UTF-8 string.

    Raises:
        FileNotFoundError: If no file exists at the resolved resource path.
    """
    path = resource_path(name, package)
    return read_text_utf8(path)


def resource_path(name: str, package: ModuleType) -> Path:
    """Resolve the filesystem path of a resource file bundled with a package.

    The returned path is not validated for existence.

    Args:
        name: Filename of the resource (e.g., `"config.json"`). May include a
            subdirectory path relative to the package root
            (e.g., `"templates/email.html"`).
        package: Package module that contains the resource.

    Returns:
        Absolute path to the resource file.
    """
    return Path(str(files(package) / name))
