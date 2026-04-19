"""Core functions for discovering dependencies and subclasses.

This module provides the core functions for discovering dependencies and subclasses
across an entire ecosystem of packages that depend on a common base dependency.
This is the foundation of pyrig's multi-package plugin architecture,
enabling automatic discovery of plugin implementations across
all dependent packages without explicit registration.
"""

import logging
from collections.abc import Generator
from functools import cache
from types import ModuleType

import pyrig
from pyrig.core.dependency_graph import DependencyGraph
from pyrig.core.introspection.modules import import_module_with_default, import_modules
from pyrig.core.introspection.packages import discover_all_subclasses_across_package

logger = logging.getLogger(__name__)


@cache
def pyrig_dependency_graph() -> DependencyGraph:
    """Get the dependency graph of installed packages depending on pyrig.

    Returns:
        A DependencyGraph instance containing all packages that depend on pyrig.
    """
    return DependencyGraph(root=pyrig.__name__)


@cache
def all_deps_depending_on_dep(dependency: ModuleType) -> tuple[ModuleType, ...]:
    """Get all packages that depend on the given dependency.

    Args:
        dependency: The dependency package to query dependents of.
        include_self: If True, includes ``dependency`` itself in the result.

    Returns:
        Tuple of imported module objects for dependent packages.
    """
    return tuple(
        import_modules(pyrig_dependency_graph().sorted_ancestors(dependency.__name__))
    )


def discover_equivalent_modules_across_dependents(
    module: ModuleType, dependency: ModuleType, until_package: ModuleType | None = None
) -> Generator[ModuleType, None, None]:
    """Find equivalent module paths across all packages that depend on a dependency.

    Core function for pyrig's multi-package architecture. Given a module path
    within a base dependency (e.g., ``pyrig.rig.configs``), discovers and imports
    the equivalent module path in every package that depends on that dependency
    (e.g., ``myapp.rig.configs``, ``other_package.rig.configs``).

    This enables automatic discovery of plugin implementations across an entire
    ecosystem of packages without requiring explicit registration.

    The discovery process:
        1. Uses ``DependencyGraph`` to find all packages depending on ``dependency``
        2. For each dependent package, constructs the equivalent module path
           by replacing the ``dependency`` prefix with the dependent package name
        3. Imports each equivalent module (creating it if the path exists)
        4. Returns all successfully imported modules in topological order

    Args:
        module: Template module whose path will be replicated across dependents.
            For example, ``pyrig.rig.configs`` would find ``myapp.rig.configs``
            in a package ``myapp`` that depends on ``pyrig``.
        dependency: The base dependency package. All packages depending on this will
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
    dependency_name = dependency.__name__
    logger.debug(
        "Discovering modules equivalent to %s in packages depending on %s",
        module_name,
        dependency_name,
    )

    for package in (dependency, *all_deps_depending_on_dep(dependency)):
        package_module_name = module_name.replace(dependency_name, package.__name__, 1)
        package_module = import_module_with_default(package_module_name)
        if package_module is not None:
            yield package_module
        if (
            isinstance(until_package, ModuleType)
            and package.__name__ == until_package.__name__
        ):
            break


def discover_subclasses_across_dependents[T: type](
    cls: T,
    dependency: ModuleType,
    package: ModuleType,
) -> Generator[T, None, None]:
    """Discover all subclasses of a class across the entire dependency ecosystem.

    Primary discovery function for pyrig's multi-package plugin architecture.
    Combines ``discover_equivalent_modules_across_dependents`` with
    ``discover_all_subclasses_across_package`` to find subclass implementations
    across all packages that depend on a base dependency.

    This is the main mechanism that enables:
        - ConfigFile subclasses to be discovered across all dependent packages
        - BuilderConfigFile implementations to be found and executed
        - Plugin-style extensibility without explicit registration

    The discovery process:
        1. Finds all equivalent modules across dependent packages using
           ``discover_equivalent_modules_across_dependents``
        2. For each module, calls ``discover_all_subclasses_across_package`` to discover
           subclasses of ``cls`` defined in that module
           (applying ``discard_parents`` and ``exclude_abstract`` filters per-module)
        3. Aggregates all discovered subclasses into a single list

    Args:
        cls: Base class to find subclasses of. All returned classes will be
            subclasses of this type (or the class itself).
        dependency: The base dependency package (e.g., ``pyrig``). The function will
            search all packages that depend on this for subclass implementations.
        package: The template module (as a ModuleType object) to replicate
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
        ...     dependency=pyrig,
        ...     package=configs
        ... )
        >>> # Returns: [PyprojectConfigFile, RuffConfigFile, MyAppConfig, ...]

    See Also:
        discover_equivalent_modules_across_dependents: Module discovery
        discover_all_subclasses_across_package: Per-module subclass discovery
        discover_leaf_subclass_across_dependents: When exactly one leaf expected
    """
    logger.debug(
        "Discovering subclasses of %s from modules in packages depending on %s",
        cls.__name__,
        dependency.__name__,
    )

    return (
        subclass
        for package in discover_equivalent_modules_across_dependents(
            module=package, dependency=dependency
        )
        for subclass in discover_all_subclasses_across_package(
            cls,
            package=package,
        )
    )
