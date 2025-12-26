"""Module and package import utilities with fallback mechanisms.

This module provides utilities for importing Python modules and packages,
including package detection, recursive package traversal, and dynamic module
importing with fallback strategies.

The utilities handle edge cases like:
    - Distinguishing between modules and packages
    - Walking package hierarchies recursively
    - Importing modules that may not exist
    - Loading modules from file paths

These are used throughout pyrig for dynamic discovery of ConfigFile subclasses,
Builder implementations, and CLI commands across multiple packages.

Example:
    >>> from pyrig.src.modules.imports import walk_package, module_is_package
    >>> import pyrig.dev.configs
    >>>
    >>> # Check if a module is a package
    >>> module_is_package(pyrig.dev.configs)
    True
    >>>
    >>> # Walk all submodules in a package
    >>> for module in walk_package(pyrig.dev.configs):
    ...     print(module.__name__)
    pyrig.dev.configs.base
    pyrig.dev.configs.gitignore
    ...

See Also:
    pyrig.src.modules.module: Module loading and path conversion
    pyrig.src.modules.path: Path utilities for modules
"""

import importlib.machinery
import importlib.util
import logging
import pkgutil
from collections.abc import Generator
from pathlib import Path
from types import ModuleType
from typing import Any

from pyrig.src.modules.module import (
    import_module_with_default,
    import_module_with_file_fallback,
)
from pyrig.src.modules.path import ModulePath

logger = logging.getLogger(__name__)


def module_is_package(obj: ModuleType) -> bool:
    """Determine if a module object represents a package.

    Checks if the given module object is a package by looking for the __path__
    attribute, which is only present in package modules.

    Args:
        obj: The module object to check

    Returns:
        True if the module is a package, False otherwise

    Note:
        This works for both regular packages and namespace packages.

    """
    return hasattr(obj, "__path__")


def import_pkg_from_dir(package_dir: Path) -> ModuleType:
    """Import a package from a directory.

    This function imports a package from a directory by creating a module
    spec and loading the module from the __init__.py file in the directory.

    Args:
        package_dir (Path): The directory containing the package to import.

    Raises:
        ValueError: If the package directory does not contain an __init__.py file.

    Returns:
        ModuleType: The imported package module.
    """
    init_path = package_dir / "__init__.py"

    package_name = ModulePath.absolute_path_to_module_name(package_dir)
    loader = importlib.machinery.SourceFileLoader(package_name, str(init_path))
    spec = importlib.util.spec_from_loader(package_name, loader, is_package=True)
    if spec is None:
        msg = f"Could not create spec for {package_dir}"
        raise ValueError(msg)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def import_pkg_with_dir_fallback(path: Path) -> ModuleType:
    """Import a package from a path.

    If pkg cannot be found via normal importlib, try to import from path.

    Args:
        path (Path): The path to the package

    Returns:
        ModuleType: The imported package module.
    """
    path = path.resolve()
    module_name = ModulePath.absolute_path_to_module_name(path)
    pkg = import_module_with_default(module_name)
    if isinstance(pkg, ModuleType):
        return pkg
    return import_pkg_from_dir(path)


def import_pkg_with_dir_fallback_with_default(
    path: Path, default: Any = None
) -> ModuleType | Any:
    """Import a package from a path, returning a default on failure.

    Args:
        path: Filesystem path to the package.
        default: Value to return if the package cannot be imported.

    Returns:
        The imported package, or `default` if import fails.
    """
    try:
        return import_pkg_with_dir_fallback(path)
    except FileNotFoundError:
        return default


def get_modules_and_packages_from_package(
    package: ModuleType,
) -> tuple[list[ModuleType], list[ModuleType]]:
    """Extract all direct subpackages and modules from a package.

    Discovers and imports all direct child modules and subpackages within
    the given package. Returns them as separate lists.

    Args:
        package: The package module to extract subpackages and modules from

    Returns:
        A tuple containing (list of subpackages, list of modules)

    Note:
        Only includes direct children, not recursive descendants.
        All discovered modules and packages are imported during this process.

    """
    modules_and_packages = list(
        pkgutil.iter_modules(package.__path__, prefix=package.__name__ + ".")
    )
    packages: list[ModuleType] = []
    modules: list[ModuleType] = []
    for _finder, name, is_pkg in modules_and_packages:
        if is_pkg:
            path = ModulePath.pkg_name_to_relative_dir_path(name)
            pkg = import_pkg_with_dir_fallback(path)
            packages.append(pkg)
        else:
            path = ModulePath.module_name_to_relative_file_path(name)
            mod = import_module_with_file_fallback(path)
            modules.append(mod)

    # make consistent order
    packages.sort(key=lambda p: p.__name__)
    modules.sort(key=lambda m: m.__name__)

    return packages, modules


def walk_package(
    package: ModuleType,
) -> Generator[tuple[ModuleType, list[ModuleType]], None, None]:
    """Recursively walk through a package and all its subpackages.

    Performs a depth-first traversal of the package hierarchy, yielding each
    package along with its direct module children.

    Args:
        package: The root package module to start walking from

    Yields:
        Tuples of (package, list of modules in package)

    Note:
        All packages and modules are imported during this process.
        The traversal is depth-first, so subpackages are fully processed
        before moving to siblings.

    """
    subpackages, submodules = get_modules_and_packages_from_package(package)
    yield package, submodules
    for subpackage in subpackages:
        yield from walk_package(subpackage)
