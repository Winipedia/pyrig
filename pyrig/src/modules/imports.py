"""Module and package import utilities with fallback mechanisms.

Provides utilities for importing modules/packages, package detection, recursive package
traversal, and dynamic importing with fallback strategies. Central to pyrig's plugin
architecture, enabling automatic discovery of ConfigFile subclasses, Builder
implementations, and CLI commands across the package dependency ecosystem.

Key functions:
    walk_package: Recursive package traversal for discovery
    import_pkg_with_dir_fallback: Import with direct file fallback
    get_modules_and_packages_from_package: Extract direct children from a package
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
    """Check if a module object represents a package.

    Packages in Python have a ``__path__`` attribute that lists the directories
    containing the package's submodules. This attribute exists for both regular
    packages (with ``__init__.py``) and namespace packages (PEP 420).

    Args:
        obj: Module object to check.

    Returns:
        True if the module has a ``__path__`` attribute (is a package),
        False otherwise (is a regular module).
    """
    return hasattr(obj, "__path__")


def import_pkg_from_dir(package_dir: Path) -> ModuleType:
    """Import a package directly from a directory path.

    Low-level import that bypasses `sys.modules` caching. Creates a module spec
    from the directory's ``__init__.py`` and executes it. Use
    ``import_pkg_with_dir_fallback`` for normal imports with fallback behavior.

    Args:
        package_dir: Directory containing the package (must have ``__init__.py``).

    Returns:
        Imported package module.

    Raises:
        FileNotFoundError: If package directory or ``__init__.py`` doesn't exist.
        ValueError: If module spec cannot be created from the path.
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
    """Import a package, falling back to direct directory import if needed.

    Primary package import function with two-stage strategy:
        1. Attempts standard import via ``import_module`` (uses ``sys.modules``)
        2. Falls back to direct file import via ``import_pkg_from_dir``

    The fallback handles packages not yet in ``sys.modules``, such as dynamically
    created packages or packages in non-standard locations.

    Args:
        path: Absolute or relative path to the package directory.
            Will be resolved to absolute before deriving module name.

    Returns:
        Imported package module.

    Raises:
        FileNotFoundError: If fallback fails and package doesn't exist.
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
    """Import a package, returning a default value if the package doesn't exist.

    Wrapper around ``import_pkg_with_dir_fallback`` that catches
    ``FileNotFoundError`` and returns a default value instead.

    Note:
        Only catches ``FileNotFoundError``. Other exceptions (``ValueError``,
        ``ImportError`` from syntax errors, etc.) will still propagate.

    Args:
        path: Path to the package directory.
        default: Value to return if the package doesn't exist. Defaults to None.

    Returns:
        The imported package module, or ``default`` if import fails due to
        missing files.
    """
    try:
        return import_pkg_with_dir_fallback(path)
    except FileNotFoundError:
        return default


def get_modules_and_packages_from_package(
    package: ModuleType,
) -> tuple[list[ModuleType], list[ModuleType]]:
    """Extract and import all direct subpackages and modules from a package.

    Uses ``pkgutil.iter_modules`` to discover direct children of the package,
    then imports each one. Subpackages and modules are returned in separate lists,
    sorted alphabetically by their fully qualified names.

    Important:
        This function imports all discovered modules as a side effect. This is
        intentional—it enables pyrig's class discovery mechanisms to find
        subclasses defined in those modules (e.g., ConfigFile implementations).

    Note:
        Only includes direct children, not recursive descendants. For full
        package tree traversal, use ``walk_package``.

    Args:
        package: Package module to extract children from. Must have a
            ``__path__`` attribute (i.e., must be a package, not a module).

    Returns:
        A tuple of ``(subpackages, modules)`` where:
            - ``subpackages``: List of imported subpackage modules, sorted by name
            - ``modules``: List of imported module objects, sorted by name
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
    """Recursively walk and import all modules in a package hierarchy.

    Performs depth-first traversal, yielding each package with its direct
    module children. Essential for pyrig's discovery system - ensures all
    modules are imported so that subclass registration (via ``__subclasses__()``)
    is complete before discovery queries.

    Used by:
        - ``get_all_subclasses``: Ensures subclasses are imported before querying
        - ``create_tests_for_package``: Generates test files for all modules
        - Session fixtures: Validates package structure and imports

    Args:
        package: Root package module to start traversal from.

    Yields:
        Tuples of (package, modules) where modules is the list of direct
        module children (not subpackages) in that package.
    """
    logger.debug("Walking package: %s", package.__name__)
    subpackages, submodules = get_modules_and_packages_from_package(package)
    yield package, submodules
    for subpackage in subpackages:
        yield from walk_package(subpackage)
