"""Package discovery, traversal, and cross-dependency subclass discovery.

Provides utilities for package creation, name conversion, recursive traversal,
and cross-dependency discovery. Uses ``DependencyGraph`` from
``pyrig.src.dependency_graph`` to find all packages that depend on a given
dependency, enabling automatic discovery of ``ConfigFile`` implementations and
``BuilderConfigFile`` subclasses across the ecosystem.
"""

import logging
from collections.abc import Callable, Sequence
from functools import cache
from pathlib import Path
from types import ModuleType
from typing import Any

from pyrig.src.dependency_graph import DependencyGraph
from pyrig.src.modules.class_ import (
    all_cls_from_module,
    all_methods_from_cls,
    discard_parent_classes,
    discover_all_subclasses,
)
from pyrig.src.modules.function import all_functions_from_module
from pyrig.src.modules.imports import (
    import_package_with_dir_fallback,
    module_is_package,
    modules_and_packages_from_package,
)
from pyrig.src.modules.module import (
    import_module_with_file_fallback,
)
from pyrig.src.modules.path import ModulePath, make_dir_with_init_file

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


def package_name_from_project_name(project_name: str) -> str:
    """Convert project name to package name (hyphens → underscores).

    Args:
        project_name: Project name.

    Returns:
        Package name.
    """
    return project_name.replace("-", "_")


def project_name_from_package_name(package_name: str) -> str:
    """Convert package name to project name (underscores → hyphens).

    Args:
        package_name: Package name.

    Returns:
        Project name.
    """
    return package_name.replace("_", "-")


def project_name_from_cwd() -> str:
    """Get project name from current directory name.

    Returns:
        Current directory name.
    """
    cwd = Path.cwd()
    return cwd.name


def package_name_from_cwd() -> str:
    """Get package name from current directory name.

    Returns:
        Package name (directory name with underscores).
    """
    return package_name_from_project_name(project_name_from_cwd())


def objs_from_obj(
    obj: Callable[..., Any] | type | ModuleType,
) -> Sequence[Callable[..., Any] | type | ModuleType]:
    """Extract contained objects from a container.

    Behavior depends on type:
    - Modules: all functions and classes
    - Packages: all direct module files (excludes subpackages)
    - Classes: all methods (excluding inherited)

    Args:
        obj: Container object.

    Returns:
        Sequence of contained objects.
    """
    if isinstance(obj, ModuleType):
        if module_is_package(obj):
            return modules_and_packages_from_package(obj)[1]
        objs: list[Callable[..., Any] | type] = []
        objs.extend(all_functions_from_module(obj))
        objs.extend(all_cls_from_module(obj))
        return objs
    if isinstance(obj, type):
        return all_methods_from_cls(obj, exclude_parent_methods=True)
    return []


@cache
def all_deps_depending_on_dep(
    dep: ModuleType, *, include_self: bool = False
) -> list[ModuleType]:
    """Get all packages that depend on the given dependency.

    Args:
        dep: The dependency package to query dependents of.
        include_self: If True, includes ``dep`` itself in the result.

    Returns:
        List of imported module objects for dependent packages.
    """
    return DependencyGraph().all_depending_on(dep, include_self=include_self)


@cache
def discover_equivalent_modules_across_dependents(
    module: ModuleType, dep: ModuleType, until_package: ModuleType | None = None
) -> list[ModuleType]:
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
    logger.debug(
        "Discovering modules equivalent to %s in packages depending on %s",
        module_name,
        dep.__name__,
    )
    packages = all_deps_depending_on_dep(dep, include_self=True)

    modules: list[ModuleType] = []
    for package in packages:
        package_module_name = module_name.replace(dep.__name__, package.__name__, 1)
        package_module_path = ModulePath.package_name_to_relative_dir_path(
            package_module_name
        )
        package_module = import_module_with_file_fallback(package_module_path)
        modules.append(package_module)
        if (
            isinstance(until_package, ModuleType)
            and package.__name__ == until_package.__name__
        ):
            break
    logger.debug(
        "Found modules equivalent to %s: %s", module_name, [m.__name__ for m in modules]
    )
    return modules


@cache
def discover_subclasses_across_dependents[T: type](
    cls: T,
    dep: ModuleType,
    load_package_before: ModuleType,
    *,
    discard_parents: bool = False,
    exclude_abstract: bool = False,
) -> list[T]:
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
        4. If ``discard_parents=True``, performs a second pass to remove any
           parent classes across the aggregated list (necessary because a class
           in package A may be a parent of a class in package B, which wouldn't
           be caught by the per-module filtering)

    Args:
        cls: Base class to find subclasses of. All returned classes will be
            subclasses of this type (or the class itself).
        dep: The base dependency package (e.g., ``pyrig``). The function will
            search all packages that depend on this for subclass implementations.
        load_package_before: The template module (as a ModuleType object) to replicate
            across dependent packages. For example, passing the ``pyrig.rig.configs``
            module would search for subclasses in ``myapp.rig.configs`` for each
            dependent package ``myapp``.
        discard_parents: If True, removes classes that have subclasses also
            in the result set. Essential for override patterns where a package
            extends a config from another package - only the leaf (most derived)
            class should be used.
        exclude_abstract: If True, removes abstract classes (those with
            unimplemented abstract methods). Typically True for discovering
            classes that will be instantiated.

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
        ...     load_package_before=configs,
        ...     discard_parents=True,
        ...     exclude_abstract=True,
        ... )
        >>> # Returns: [PyprojectConfigFile, RuffConfigFile, MyAppConfig, ...]

    Note:
        When ``discard_parents=True``, the filtering is performed twice: once
        within each ``discover_all_subclasses`` call (per-module) and once after
        aggregation (cross-module). The second pass is essential because a
        parent class from module A and its child from module B would both
        survive the per-module filtering.

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
    subclasses: list[T] = []
    for package in discover_equivalent_modules_across_dependents(
        load_package_before, dep
    ):
        subclasses.extend(
            discover_all_subclasses(
                cls,
                load_package_before=package,
                discard_parents=discard_parents,
                exclude_abstract=exclude_abstract,
            )
        )
    # as these are different modules and pks we need to discard parents again
    if discard_parents:
        logger.debug("Discarding parent classes. Only keeping leaf classes...")
        subclasses = discard_parent_classes(subclasses)
    logger.debug(
        "Found final leaf subclasses of %s: %s",
        cls.__name__,
        [c.__name__ for c in subclasses],
    )
    return subclasses


@cache
def discover_leaf_subclass_across_dependents[T: type](
    cls: T, dep: ModuleType, load_package_before: ModuleType
) -> T:
    """Discover the single deepest subclass in the inheritance hierarchy.

    Specialized discovery function for cases where exactly one "final" subclass
    is expected across the entire dependency ecosystem. Used when a base class
    should have a single active implementation determined by the inheritance
    chain.

    This is typically invoked via ``DependencySubclass.L`` to find the
    most-derived version of a class. For example, if:
        - ``pyrig`` defines ``PyprojectConfigFile``
        - ``mylib`` extends it as ``MyLibPyprojectConfigFile``
        - ``myapp`` extends that as ``MyAppPyprojectConfigFile``

    Then this function returns ``MyAppPyprojectConfigFile`` as the single leaf.

    The discovery process:
        1. Calls ``discover_subclasses_across_dependents`` with
           ``discard_parents=True`` to get only leaf classes
        2. Validates that exactly one leaf class was found
        3. Returns that single leaf class

    Args:
        cls: Base class to find the leaf subclass of.
        dep: The base dependency package (e.g., ``pyrig``).
        load_package_before: Template module path to replicate across dependents.

    Returns:
        The single leaf subclass type (deepest in inheritance tree).
        May be abstract - use ``exclude_abstract`` in the caller if needed.

    Raises:
        ValueError: If multiple leaf classes are found. This indicates an
            ambiguous inheritance structure where two classes both extend
            the same parent without one extending the other.
        IndexError: If no subclasses are found (empty result from discovery).

    Example:
        >>> # Find the final PyprojectConfigFile implementation
        >>> leaf = discover_leaf_subclass_across_dependents(
        ...     cls=PyprojectConfigFile,
        ...     dep=pyrig,
        ...     load_package_before=configs,
        ... )
        >>> # Returns the most-derived PyprojectConfigFile subclass

    Note:
        Abstract classes are NOT excluded - the leaf may be abstract if no
        concrete implementation exists. This is intentional for cases where
        the leaf class defines the interface but concrete instantiation
        happens elsewhere.

    See Also:
        discover_subclasses_across_dependents: General multi-subclass discovery
        DependencySubclass.L: Direct caller of this function
    """
    classes = discover_subclasses_across_dependents(
        cls=cls,
        dep=dep,
        load_package_before=load_package_before,
        discard_parents=True,
        exclude_abstract=False,
    )
    # raise if more than one final leaf
    if len(classes) > 1:
        msg = (
            f"Multiple final leaves found for {cls.__name__} "
            f"in {load_package_before.__name__}: {classes}"
        )
        raise ValueError(msg)
    leaf = classes[0]
    logger.debug("Found final leaf of %s: %s", cls.__name__, leaf.__name__)
    return leaf
