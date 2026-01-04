"""Module and package import utilities with fallback mechanisms.

Provides utilities for importing modules/packages, package detection, recursive package
traversal, and dynamic importing with fallback strategies. Used for dynamic discovery
of ConfigFile subclasses, BuilderConfigFile implementations, and CLI commands across
packages.
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
    """Check if a module is a package (has __path__ attribute).

    Args:
        obj: Module object to check.

    Returns:
        True if module is a package.

    Note:
        Works for both regular and namespace packages.
    """
    return hasattr(obj, "__path__")


def import_pkg_from_dir(package_dir: Path) -> ModuleType:
    """Import a package from a directory.

    Args:
        package_dir: Directory containing the package.

    Returns:
        Imported package module.

    Raises:
        ValueError: If spec cannot be created.
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
    """Import a package from a path with directory fallback.

    Args:
        path: Path to the package.

    Returns:
        Imported package module.
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
    """Import a package from a path, returning default on failure.

    Args:
        path: Path to the package.
        default: Value to return if import fails.

    Returns:
        Imported package or default.
    """
    try:
        return import_pkg_with_dir_fallback(path)
    except FileNotFoundError:
        return default


def get_modules_and_packages_from_package(
    package: ModuleType,
) -> tuple[list[ModuleType], list[ModuleType]]:
    """Extract all direct subpackages and modules from a package.

    Args:
        package: Package module to extract from.

    Returns:
        Tuple of (subpackages list, modules list).

    Note:
        Only includes direct children, not recursive descendants.
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

    Depth-first traversal of package hierarchy.

    Args:
        package: Root package module.

    Yields:
        Tuples of (package, list of modules in package).
    """
    logger.debug("Walking package: %s", package.__name__)
    subpackages, submodules = get_modules_and_packages_from_package(package)
    yield package, submodules
    for subpackage in subpackages:
        yield from walk_package(subpackage)
