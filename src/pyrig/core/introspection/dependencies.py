"""Cross-package module and subclass discovery for the pyrig ecosystem.

Provides utilities to locate equivalent module paths and collect subclass
implementations across all installed packages that depend on a common base
dependency.
"""

import logging
from collections.abc import Iterator
from functools import cache
from itertools import chain
from types import ModuleType

from pyrig.core.dependency_graph import DependencyGraph
from pyrig.core.introspection.modules import (
    import_module_with_default,
    import_modules,
    root_module,
)
from pyrig.core.introspection.packages import discover_all_subclasses_across_package

logger = logging.getLogger(__name__)


def discover_subclasses_across_dependencies[T](
    cls: type[T],
    package: ModuleType,
) -> Iterator[type[T]]:
    """Yield subclasses of `cls` across `package` and dependent packages.

    The primary entry point for pyrig's plugin-style subclass discovery. Starting
    with `package` itself and then each installed package that depends on
    `package`'s root package, locate the module that corresponds to `package`
    within each dependent (via [discover_equivalent_modules_across_dependents][])
    and collect every subclass of `cls` defined there.

    This enables subsystems built on
    [DependencySubclass][pyrig.core.dependency_subclass.DependencySubclass] to
    automatically find all concrete implementations across the entire installed
    ecosystem without requiring explicit registration.

    Args:
        cls: Base class whose subclasses should be discovered.
        package: Template module whose dotted path is replicated across dependent
            packages to locate the modules to search. The root of this module
            (e.g., `pyrig` for `pyrig.rig.configs`) is used to find all
            dependent packages. For example, passing `pyrig.rig` would search
            `<pkg>.rig` in each dependent package.

    Yields:
        Subclass types of `cls` discovered across `package` and all dependent
        packages, in dependency order (base package first, then dependents).
    """
    logger.debug(
        "Discovering subclasses of %s from modules in packages depending on %s",
        cls.__name__,
        package.__name__,
    )

    return (
        subclass
        for pkg in chain(
            (package,),
            discover_equivalent_modules_across_dependents(module=package),
        )
        for subclass in discover_all_subclasses_across_package(
            cls,
            package=pkg,
        )
    )


def discover_equivalent_modules_across_dependents(
    module: ModuleType,
) -> Iterator[ModuleType]:
    """Yield the equivalent module from every package that depends on `module`'s root.

    Given a module (e.g., `pyrig.rig.configs`), infers the root package
    (e.g., `pyrig`), then constructs the equivalent dotted path in each package
    that depends on that root (e.g., `myapp.rig.configs`), imports it if it
    exists, and yields it.

    The root package itself is not included in results — only its dependents are
    iterated. The path transformation replaces the first occurrence of the root
    package name in `module.__name__` with each dependent package's name, so a
    consistent directory structure across the ecosystem is assumed.

    Args:
        module: Template module whose path pattern is replicated in each dependent
            package (e.g., `pyrig.core` → `<pkg>.core` for every dependent).
            The root of this module is used to discover dependent packages.

    Yields:
        Successfully imported module objects in dependency order. Packages whose
        equivalent module path cannot be imported are silently skipped.
    """
    dependency = root_module(module)
    logger.debug(
        "Discovering modules equivalent to %s in packages depending on %s",
        module.__name__,
        dependency.__name__,
    )

    for package in deps_depending_on_dep(dependency):
        package_module_name = module.__name__.replace(
            dependency.__name__, package.__name__, 1
        )
        package_module = import_module_with_default(package_module_name)
        if package_module is not None:
            yield package_module


@cache
def deps_depending_on_dep(dependency: ModuleType) -> tuple[ModuleType, ...]:
    """Return all installed packages that depend on `dependency`, as module objects.

    Find every installed package that depends on `dependency` (directly or
    transitively), import them, and return the result as a tuple in dependency
    order. The result is cached per unique `dependency` argument.

    Args:
        dependency: The package whose dependents should be discovered.

    Returns:
        Tuple of imported module objects for all packages that depend on
        `dependency`. Does not include `dependency` itself.
    """
    return tuple(
        import_modules(
            DependencyGraph.cached(root=dependency.__name__).sorted_ancestors(
                dependency.__name__
            )
        )
    )
