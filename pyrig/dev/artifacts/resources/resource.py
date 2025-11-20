"""Provides a simple func for getting resources."""

from importlib.resources import as_file, files
from pathlib import Path
from types import ModuleType


def get_resource_path(name: str, package: ModuleType) -> Path:
    """Get the path to a resource.

    Uses importlib.resources to get the path to a resource.
    Also usefule bc it handles MEIPASS for us.

    Args:
        name: The name of the resource with extension
        package: The package that contains the resource

    Returns:
        The path to the resource
    """
    resource_path = files(package) / name
    with as_file(resource_path) as path:
        return path
