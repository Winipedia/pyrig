"""Module and package import utilities with fallback mechanisms.

Provides utilities for importing modules/packages, package detection, recursive package
traversal, and dynamic importing with fallback strategies. Central to pyrig's plugin
architecture, enabling automatic discovery of ConfigFile subclasses, Builder
implementations, and CLI commands across the package dependency ecosystem.

Key functions:
    walk_package: Recursive package traversal for discovery
    import_package_with_dir_fallback: Import with direct file fallback
    iter_modules: Extract direct children from a package
"""

import importlib.machinery
import importlib.util
import logging
import pkgutil
import sys
from collections.abc import Generator
from importlib import import_module
from pathlib import Path
from types import ModuleType

from pyrig.src.modules.module import (
    import_module_with_default,
)
from pyrig.src.modules.path import ModulePath

logger = logging.getLogger(__name__)


def module_is_package(obj: ModuleType) -> bool:
    """Check if a module object represents a package.

    Packages in Python have a ``__path__`` attribute that lists the directories
    containing the package's submodules. This attribute exists for both regular
    packages (with ``__init__.py``) and namespace packages.

    Args:
        obj: Module object to check.

    Returns:
        True if the module has a ``__path__`` attribute (is a package),
        False otherwise (is a regular module).
    """
    return hasattr(obj, "__path__")


def import_package_from_dir(package_dir: Path) -> ModuleType:
    """Import a package directly from a directory path.

    Low-level import that bypasses `sys.modules` caching. Creates a module spec
    from the directory's ``__init__.py`` and executes it. Use
    ``import_package_with_dir_fallback`` for normal imports with fallback behavior.

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
    sys.modules[package_name] = module
    return module


def import_package_with_dir_fallback(path: Path) -> ModuleType:
    """Import a package, falling back to direct directory import if needed.

    Primary package import function with two-stage strategy:
        1. Attempts standard import via
            ``import_module_with_default`` (uses ``sys.modules``)
        2. Falls back to direct file import via ``import_package_from_dir``

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
    package = import_module_with_default(module_name)
    if isinstance(package, ModuleType):
        return package
    return import_package_from_dir(path)


def walk_package(
    package: ModuleType,
) -> Generator[tuple[ModuleType, bool], None, None]:
    """Recursively walk and import all modules in a package hierarchy.

    Performs depth-first traversal, yielding each package with its direct
    module children. Essential for pyrig's discovery system - ensures all
    modules are imported so that subclass registration (via ``__subclasses__()``)
    is complete before discovery queries.

    See Also:
        `pyrig.src.modules.class_.discover_all_subclasses`: Subclass discovery.
        `pyrig.rig.cli.commands.create_tests.create_tests_for_package`: Test
            generation.

    Args:
        package: Root package module to start traversal from.

    Yields:
        Tuples of (package, modules) where modules is the list of direct
        module children (not subpackages) in that package.
    """
    yield package, True
    for module, is_package in iter_modules(package):
        if is_package:
            yield from walk_package(module)
        else:
            yield module, False


def iter_modules(
    package: ModuleType,
) -> Generator[tuple[ModuleType, bool], None, None]:
    """Extract and import all direct subpackages and modules from a package.

    Uses ``pkgutil.iter_modules`` to discover direct children of the package,
    then imports each one. Subpackages and modules are returned in separate lists,
    sorted alphabetically by their fully qualified names.

    Note:
        This function imports all discovered modules as a side effect. This is
        intentional — it enables pyrig's class discovery mechanisms to find
        subclasses defined in those modules (e.g., ``ConfigFile`` implementations).

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
    for _finder, name, is_package in pkgutil.iter_modules(
        package.__path__, prefix=package.__name__ + "."
    ):
        mod = import_module(name)
        yield mod, is_package
