"""Package discovery, traversal, and cross-dependency subclass discovery.

Provides utilities for package creation, name conversion, recursive traversal,
and cross-dependency discovery. Uses ``DependencyGraph`` from
``pyrig.src.dependency_graph`` to find all packages that depend on a given
dependency, enabling automatic discovery of ``ConfigFile`` implementations and
``BuilderConfigFile`` subclasses across the ecosystem.
"""

import logging
from collections.abc import Generator
from functools import cache
from importlib import import_module
from pathlib import Path
from types import ModuleType

from pyrig.src.dependency_graph import DependencyGraph
from pyrig.src.modules.class_ import (
    discover_all_subclasses,
)
from pyrig.src.modules.imports import (
    import_package_with_dir_fallback,
)
from pyrig.src.modules.module import (
    import_modules,
)
from pyrig.src.modules.path import make_dir_with_init_file

logger = logging.getLogger(__name__)


def create_package(path: Path) -> ModuleType:
    """Create a Python package directory and import it.

    Creates the directory structure (including __init__.py) and imports the
    resulting package. Used for dynamically creating package structures at runtime.

    Args:
        path: Directory path where the package should be created.
            Must not end with __init__.py (provide the directory path only).

    Returns:
        The imported package module object.

    Raises:
        ValueError: If path is the current working directory (CWD).
            Creating a package at CWD would interfere with the project structure.
    """
    if path == Path.cwd():
        msg = f"Cannot create package {path=} because it is the CWD"
        raise ValueError(msg)
    make_dir_with_init_file(path)

    return import_package_with_dir_fallback(path)


@cache
def all_deps_depending_on_dep(dep: ModuleType) -> tuple[ModuleType, ...]:
    """Get all packages that depend on the given dependency.

    Args:
        dep: The dependency package to query dependents of.
        include_self: If True, includes ``dep`` itself in the result.

    Returns:
        Tuple of imported module objects for dependent packages.
    """
    return tuple(import_modules(DependencyGraph().sorted_ancestors(dep.__name__)))


def discover_equivalent_modules_across_dependents(
    module: ModuleType, dep: ModuleType, until_package: ModuleType | None = None
) -> Generator[ModuleType, None, None]:
    """Find equivalent module paths across all packages that depend on a dependency.

    Core function for pyrig's multi-package architecture. Given a module path
    within a base dependency (e.g., ``pyrig.rig.configs``), discovers and imports
    the equivalent module path in every package that depends on that dependency
    (e.g., ``myapp.rig.configs``, ``other_package.rig.configs``).

    This enables automatic discovery of plugin implementations across an entire
    ecosystem of packages without requiring explicit registration.

    The discovery process:
        1. Uses ``DependencyGraph`` to find all packages depending on ``dep``
        2. For each dependent package, constructs the equivalent module path
           by replacing the ``dep`` prefix with the dependent package name
        3. Imports each equivalent module (creating it if the path exists)
        4. Returns all successfully imported modules in topological order

    Args:
        module: Template module whose path will be replicated across dependents.
            For example, ``pyrig.rig.configs`` would find ``myapp.rig.configs``
            in a package ``myapp`` that depends on ``pyrig``.
        dep: The base dependency package. All packages depending on this will
            be searched for equivalent modules.
        until_package: Optional package to stop at. When provided, stops iterating
            through dependents once this package is reached (inclusive).
            Useful for limiting discovery scope.

    Returns:
        List of imported module objects from all dependent packages, in
        topological order (base dependency first, then dependents in order).

    Example:
        >>> # Find all rig.configs modules across pyrig ecosystem
        >>> from pyrig.rig import configs
        >>> import pyrig
        >>> modules = discover_equivalent_modules_across_dependents(configs, pyrig)
        >>> # Returns: [pyrig.rig.configs, myapp.rig.configs, other_package.rig.configs]

    Note:
        The module path transformation is a simple string replacement of the
        first occurrence of ``dep.__name__`` with each dependent package name.
        This assumes consistent package structure across the ecosystem.

    See Also:
        DependencyGraph.all_depending_on: Finds dependent packages
        discover_subclasses_across_dependents: Uses this to find subclasses
    """
    module_name = module.__name__
    dependency_name = dep.__name__
    logger.debug(
        "Discovering modules equivalent to %s in packages depending on %s",
        module_name,
        dependency_name,
    )

    for package in (dep, *all_deps_depending_on_dep(dep)):
        package_module_name = module_name.replace(dependency_name, package.__name__, 1)
        package_module = import_module(package_module_name)
        yield package_module
        if (
            isinstance(until_package, ModuleType)
            and package.__name__ == until_package.__name__
        ):
            break


def discover_subclasses_across_dependents[T: type](
    cls: T,
    dep: ModuleType,
    load_package_before: ModuleType,
) -> Generator[T, None, None]:
    """Discover all subclasses of a class across the entire dependency ecosystem.

    Primary discovery function for pyrig's multi-package plugin architecture.
    Combines ``discover_equivalent_modules_across_dependents`` with
    ``discover_all_subclasses`` to find subclass implementations across all
    packages that depend on a base dependency.

    This is the main mechanism that enables:
        - ConfigFile subclasses to be discovered across all dependent packages
        - BuilderConfigFile implementations to be found and executed
        - Plugin-style extensibility without explicit registration

    The discovery process:
        1. Finds all equivalent modules across dependent packages using
           ``discover_equivalent_modules_across_dependents``
        2. For each module, calls ``discover_all_subclasses`` to discover
           subclasses of ``cls`` defined in that module
           (applying ``discard_parents`` and ``exclude_abstract`` filters per-module)
        3. Aggregates all discovered subclasses into a single list

    Args:
        cls: Base class to find subclasses of. All returned classes will be
            subclasses of this type (or the class itself).
        dep: The base dependency package (e.g., ``pyrig``). The function will
            search all packages that depend on this for subclass implementations.
        load_package_before: The template module (as a ModuleType object) to replicate
            across dependent packages. For example, passing the ``pyrig.rig.configs``
            module would search for subclasses in ``myapp.rig.configs`` for each
            dependent package ``myapp``.

    Returns:
        List of discovered subclass types. Order is based on topological
        dependency order (base package classes first, then dependents).

    Example:
        >>> # Discover all ConfigFile implementations across ecosystem
        >>> from pyrig.rig import configs
        >>> import pyrig
        >>> subclasses = discover_subclasses_across_dependents(
        ...     cls=ConfigFile,
        ...     dep=pyrig,
        ...     load_package_before=configs
        ... )
        >>> # Returns: [PyprojectConfigFile, RuffConfigFile, MyAppConfig, ...]

    See Also:
        discover_equivalent_modules_across_dependents: Module discovery
        discover_all_subclasses: Per-module subclass discovery
        discover_leaf_subclass_across_dependents: When exactly one leaf expected
    """
    logger.debug(
        "Discovering subclasses of %s from modules in packages depending on %s",
        cls.__name__,
        dep.__name__,
    )

    return (
        subclass
        for package in discover_equivalent_modules_across_dependents(
            load_package_before, dep
        )
        for subclass in discover_all_subclasses(
            cls,
            load_package_before=package,
        )
    )
