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
import pkgutil
import re
import sys
from collections.abc import Generator, Iterable
from importlib import import_module
from pathlib import Path
from types import ModuleType

from pyrig.core.modules.module import (
    import_module_with_default,
)


def import_package_from_dir(path: Path, name: str) -> ModuleType:
    """Import a package directly from a directory path.

    Low-level import that bypasses `sys.modules` caching. Creates a module spec
    from the directory's ``__init__.py`` and executes it. Use
    ``import_package_with_dir_fallback`` for normal imports with fallback behavior.

    Args:
        path: Directory containing the package (must have ``__init__.py``).
        name: The dotted module name for the package.


    Returns:
        Imported package module.

    Raises:
        FileNotFoundError: If package directory or ``__init__.py`` doesn't exist.
        ImportError: If module spec cannot be created from the path.
    """
    init_path = path / "__init__.py"

    loader = importlib.machinery.SourceFileLoader(
        fullname=name, path=init_path.as_posix()
    )
    spec = importlib.util.spec_from_loader(name=name, loader=loader, is_package=True)
    if spec is None:
        msg = f"Could not create spec for {init_path}"
        raise ImportError(msg)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    sys.modules[name] = module
    return module


def import_package_with_dir_fallback(path: Path, name: str) -> ModuleType:
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
        name: The dotted module name for the package.

    Returns:
        Imported package module.

    Raises:
        FileNotFoundError: If fallback fails and package doesn't exist.
    """
    path = path.resolve()
    package = import_module_with_default(name)
    if isinstance(package, ModuleType):
        return package
    return import_package_from_dir(path, name)


def walk_package(
    package: ModuleType,
    exclude: Iterable[str] = (),
) -> Generator[tuple[ModuleType, bool], None, None]:
    """Recursively walk and import all modules in a package hierarchy.

    Performs depth-first traversal, yielding each package with its direct
    module children. Essential for pyrig's discovery system - ensures all
    modules are imported so that subclass registration (via ``__subclasses__()``)
    is complete before discovery queries.

    It does not include the given root package itself in the output,
    only its children and their descendants.

    See Also:
        `pyrig.src.modules.class_.discover_all_subclasses`: Subclass discovery.
        `pyrig.rig.cli.commands.make_tests.make_tests_for_package`: Test
            generation.

    Args:
        package: Root package module to start traversal from.
        exclude: Optional iterable of regex patterns to exclude from results.
        Patterns are matched against fully qualified module names
        (e.g., "pyrig.rig.configs.base").

    Yields:
        Tuples of (package, modules) where modules is the list of direct
        module children (not subpackages) in that package.
    """
    for module, is_package in iter_modules(package, exclude=exclude):
        if is_package:
            yield module, True
            yield from walk_package(module)
        else:
            yield module, False


def iter_modules(
    package: ModuleType,
    exclude: Iterable[str] = (),
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
        exclude: Optional iterable of regex patterns to exclude from results.
        Patterns are matched against fully qualified module names
        (e.g., "pyrig.rig.configs.base").

    Returns:
        A tuple of ``(subpackages, modules)`` where:
            - ``subpackages``: List of imported subpackage modules, sorted by name
            - ``modules``: List of imported module objects, sorted by name
    """
    for _finder, name, is_package in pkgutil.iter_modules(
        package.__path__, prefix=package.__name__ + "."
    ):
        if any(re.search(pattern, name) for pattern in exclude):
            continue
        mod = import_module(name)
        yield mod, is_package
