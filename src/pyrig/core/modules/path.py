"""Path utilities for module and package management.

Runtime utilities for working with Python module and package paths. This module
provides bidirectional conversions between dotted module names and filesystem paths,
support for frozen environments (PyInstaller), and package structure creation.

Part of the ``pyrig.src.modules`` subpackage.

Key Components:
    ModulePath: Static utility class for path/module name conversions.
    make_init_modules_for_package: Recursively create __init__.py files.
    make_dir_with_init_file: Create a directory as a Python package.
    make_init_module: Create a single __init__.py file.
    make_package_dir: Create __init__.py files up the directory hierarchy.
"""

from pathlib import Path
from types import ModuleType


def module_file_path(module: ModuleType) -> Path:
    """Get the file path of an imported module.

    Args:
        module: An imported Python module.

    Returns:
        Absolute path to the module's source file.

    Raises:
        ValueError: If the module has no __file__ attribute (e.g., built-in
            modules or namespace packages).
    """
    file = module.__file__
    if file is None:
        msg = f"Module {module} has no __file__"
        raise AttributeError(msg)
    return Path(file)


def package_dir_path(package: ModuleType) -> Path:
    """Get the directory path of an imported package.

    Args:
        package: An imported Python package (a module with an __init__.py).

    Returns:
        Absolute path to the package's directory (parent of __init__.py).

    Raises:
        ValueError: If the module has no __file__ attribute (e.g., built-in
            modules or namespace packages).
    """
    return module_file_path(package).parent


def package_name_as_path(name: str) -> Path:
    """Convert a dotted package name to a relative directory path.

    Args:
        name: Dotted Python package name (e.g., "package.subpackage").

    Returns:
        Relative path to the package directory (e.g., "package/subpackage").
    """
    return Path(*name.split("."))


def module_name_as_path(name: str) -> Path:
    """Convert a dotted module name to a relative file path.

    Args:
        name: Dotted Python module name (e.g., "package.subpackage.module").

    Returns:
        Relative path to the module file (e.g., "package/subpackage/module.py").
    """
    return package_name_as_path(name).with_suffix(".py")


def path_as_module_name(path: Path) -> str:
    """Convert a relative file path to a dotted module name.

    Args:
        path: Relative file path (e.g., "package/subpackage/module.py").

    Returns:
        Dotted Python module name (e.g., "package.subpackage.module").
    """
    # Remove the .py suffix and convert to dotted name
    return ".".join(path.with_suffix("").parts)
