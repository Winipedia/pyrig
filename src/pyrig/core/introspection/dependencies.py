"""Cross-package module and subclass discovery for the pyrig ecosystem.

Provides utilities to locate equivalent module paths and collect subclass
implementations across all installed packages that depend on a common base
dependency.
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


def discover_subclasses_across_dependents[T: type](
    cls: T,
    dependency: ModuleType,
    package: ModuleType,
) -> Generator[T, None, None]:
    """Yield all subclasses of ``cls`` across packages that depend on ``dependency``.

    The primary entry point for pyrig's plugin-style subclass discovery. For
    ``dependency`` itself and each installed package that depends on ``dependency``,
    this function locates the module that corresponds to ``package`` within that
    package and collects every subclass of ``cls`` defined there.

    This enables subsystems such as ``ConfigFile`` and ``Tool`` to automatically
    find all concrete implementations across the entire installed ecosystem
    without requiring explicit registration.

    Args:
        cls: Base class whose subclasses should be discovered.
        dependency: The base dependency package (e.g., ``pyrig``). This package
            itself and all installed packages that depend on it are searched.
        package: Template module whose dotted path is replicated across dependent
            packages to locate the modules to search. For example, passing
            ``pyrig.rig`` would search ``<pkg>.rig`` in each dependent package.

    Yields:
        Subclass types of ``cls`` discovered across all dependent packages, in
        topological dependency order (base package first, then dependents).

    Example:
        >>> from pyrig.rig.configs.base.config_file import ConfigFile
        >>> from pyrig.rig import configs
        >>> import pyrig
        >>> subclasses = list(discover_subclasses_across_dependents(
        ...     cls=ConfigFile,
        ...     dependency=pyrig,
        ...     package=configs,
        ... ))
        >>> # Returns concrete ConfigFile implementations across the pyrig ecosystem.
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


def discover_equivalent_modules_across_dependents(
    module: ModuleType, dependency: ModuleType, until_package: ModuleType | None = None
) -> Generator[ModuleType, None, None]:
    """Yield the equivalent module from ``dependency`` and every dependent package.

    Given a module within ``dependency`` (e.g., ``pyrig.rig.configs``), constructs
    the equivalent dotted path in each package that depends on ``dependency``
    (e.g., ``myapp.rig.configs``), imports it if it exists, and yields it.

    Discovery always starts with ``dependency`` itself before iterating over its
    dependents in topological order. The path transformation replaces the first
    occurrence of ``dependency.__name__`` in ``module.__name__`` with each
    dependent package's name, so a consistent directory structure across the
    ecosystem is assumed.

    Args:
        module: Template module whose path pattern is replicated in each dependent
            package (e.g., ``pyrig.core`` → ``<pkg>.core`` for every dependent).
        dependency: The base dependency package. Both this package and all
            packages that depend on it are iterated.
        until_package: If provided, iteration stops after this package is reached
            (inclusive), whether or not its equivalent module was found. Useful for
            scoping discovery to a subset of the ecosystem.

    Yields:
        Successfully imported module objects in topological order, starting with
        the module from ``dependency`` itself. Packages whose equivalent module
        path cannot be imported are silently skipped.

    Example:
        >>> import pyrig
        >>> from pyrig import core
        >>> modules = list(discover_equivalent_modules_across_dependents(core, pyrig))
        >>> # Includes pyrig.core and the corresponding module in each dependent
        >>> # package.
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
        if package is until_package:
            break


@cache
def all_deps_depending_on_dep(dependency: ModuleType) -> tuple[ModuleType, ...]:
    """Return all installed packages that depend on ``dependency``, as module objects.

    Uses the pyrig dependency graph to find every installed package that depends
    on ``dependency`` (directly or transitively), imports them, and returns the
    result as a tuple in topological order (packages with fewer transitive
    dependencies appear first). The result is cached per unique ``dependency``
    argument.

    Args:
        dependency: The package whose dependents should be discovered.

    Returns:
        Tuple of imported module objects for all packages that depend on
        ``dependency``. Does not include ``dependency`` itself.
    """
    return tuple(
        import_modules(pyrig_dependency_graph().sorted_ancestors(dependency.__name__))
    )


@cache
def pyrig_dependency_graph() -> DependencyGraph:
    """Return the cached dependency graph rooted at the ``pyrig`` package.

    Builds and caches a ``DependencyGraph`` containing only ``pyrig`` and all
    installed packages that depend on it. Constructed at most once per process.

    Returns:
        A ``DependencyGraph`` rooted at ``pyrig``.
    """
    return DependencyGraph(root=pyrig.__name__)
