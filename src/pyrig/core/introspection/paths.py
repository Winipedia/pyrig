"""Conversions between dotted Python names, filesystem paths, and module objects."""

from pathlib import Path
from types import ModuleType


def module_file_path(module: ModuleType) -> Path:
    """Return the path recorded in an imported module's `__file__` attribute.

    Args:
        module: An imported Python module.

    Returns:
        The module's file path.

    Raises:
        AttributeError: If the module has no `__file__` attribute (e.g., a
            built-in module) or that attribute is `None` (e.g., a
            namespace package).
    """
    file = module.__file__
    if file is None:
        msg = f"module {module} has no __file__"
        raise AttributeError(msg)
    return Path(file)


def module_name_as_path(name: str) -> Path:
    """Convert a dotted module name to a relative `.py` file path.

    Args:
        name: Dotted Python module name (e.g., `"package.subpackage.module"`).

    Returns:
        Relative path to the module's source file
        (e.g., `Path("package/subpackage/module.py")`).
    """
    return package_name_as_path(name).with_suffix(".py")


def package_name_as_path(name: str) -> Path:
    """Convert a dotted package name to a relative directory path.

    Args:
        name: Dotted Python package name (e.g., `"package.subpackage"`).

    Returns:
        Relative path to the package directory
        (e.g., `Path("package/subpackage")`).
    """
    return Path(*name.split("."))
