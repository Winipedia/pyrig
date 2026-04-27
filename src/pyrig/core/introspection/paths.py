"""Conversions between Python module names, filesystem paths, and module objects.

Provides utilities for translating dotted module names to filesystem paths,
and for resolving the source file or directory of an imported module object.
"""

from pathlib import Path
from types import ModuleType


def package_dir_path(package: ModuleType) -> Path:
    """Get the directory of an imported package.

    Args:
        package: An imported Python package (a module with an ``__init__.py``).

    Returns:
        Absolute path to the package directory (the parent of the package's
        ``__init__.py`` file).

    Raises:
        AttributeError: If the package's ``__file__`` attribute is ``None``
            (e.g., built-in modules or namespace packages).
    """
    return module_file_path(package).parent


def module_file_path(module: ModuleType) -> Path:
    """Get the source file path of an imported module.

    Args:
        module: An imported Python module.

    Returns:
        Absolute path to the module's ``.py`` source file.

    Raises:
        AttributeError: If the module's ``__file__`` attribute is ``None``
            (e.g., built-in modules or namespace packages).
    """
    file = module.__file__
    if file is None:
        msg = f"Module {module} has no __file__"
        raise AttributeError(msg)
    return Path(file)


def module_name_as_path(name: str) -> Path:
    """Convert a dotted module name to a relative ``.py`` file path.

    Args:
        name: Dotted Python module name (e.g., ``"package.subpackage.module"``).

    Returns:
        Relative path to the module's source file
        (e.g., ``Path("package/subpackage/module.py")``).
    """
    return package_name_as_path(name).with_suffix(".py")


def package_name_as_path(name: str) -> Path:
    """Convert a dotted package name to a relative directory path.

    Args:
        name: Dotted Python package name (e.g., ``"package.subpackage"``).

    Returns:
        Relative path to the package directory
        (e.g., ``Path("package/subpackage")``).
    """
    return Path(*name.split("."))


def path_as_module_name(path: Path) -> str:
    """Convert a relative file path to a dotted module name.

    Strips the ``.py`` extension if present, then joins the path parts with
    dots. Paths without an extension are handled the same as those with
    ``.py``.

    Args:
        path: Relative file path (e.g., ``Path("package/subpackage/module.py")``
            or ``Path("package/subpackage/module")``).

    Returns:
        Dotted Python module name (e.g., ``"package.subpackage.module"``).
    """
    return ".".join(path.with_suffix("").parts)
