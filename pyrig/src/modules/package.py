"""Package discovery, traversal, and dependency graph analysis.

Provides utilities for package discovery, recursive traversal, and dependency graph
analysis. The `DependencyGraph` class enables automatic discovery of all packages
that depend on pyrig, allowing discovery of ConfigFile implementations and
BuilderConfigFile subclasses across the ecosystem.
"""

import importlib.metadata
import logging
import re
from collections.abc import Callable, Iterable, Sequence
from functools import cache
from pathlib import Path
from types import ModuleType
from typing import Any

from pyrig.src.graph import DiGraph
from pyrig.src.modules.class_ import (
    discard_parent_classes,
    get_all_cls_from_module,
    get_all_methods_from_cls,
    get_all_subclasses,
)
from pyrig.src.modules.function import get_all_functions_from_module
from pyrig.src.modules.imports import (
    get_modules_and_packages_from_package,
    import_pkg_with_dir_fallback,
    module_is_package,
)
from pyrig.src.modules.module import (
    import_module_with_default,
    import_module_with_file_fallback,
)
from pyrig.src.modules.path import ModulePath, make_dir_with_init_file

logger = logging.getLogger(__name__)

# Pre-compiled regex for parsing package names from requirement strings.
# Matches everything before the first version specifier (>, <, =, [, ;, etc.)
# Allows alphanumeric, underscore, hyphen, and period (for namespace packages).
# Performance: compiled once at module load vs. per-call compilation.
# Used by DependencyGraph and PyprojectConfigFile.L.
PACKAGE_REQ_NAME_SPLIT_PATTERN = re.compile(r"[^a-zA-Z0-9_.-]")


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

    return import_pkg_with_dir_fallback(path)


class DependencyGraph(DiGraph):
    """Directed graph of installed Python package dependencies.

    Nodes are package names, edges represent dependency relationships.
    Built automatically on instantiation by scanning installed distributions.
    Central to pyrig's multi-package discovery system.
    """

    def __init__(self) -> None:
        """Initialize and build the dependency graph from installed distributions."""
        super().__init__()
        self.build()

    def build(self) -> None:
        """Build the graph from installed Python distributions."""
        logger.debug("Building dependency graph from installed distributions")
        for dist in importlib.metadata.distributions():
            name = self.parse_distname_from_metadata(dist)
            self.add_node(name)

            requires = dist.requires or []
            for req in requires:
                dep = self.parse_pkg_name_from_req(req)
                if dep:
                    self.add_edge(name, dep)  # package → dependency
        logger.debug("Dependency graph built with %d packages", len(self.nodes()))

    @staticmethod
    def parse_distname_from_metadata(dist: importlib.metadata.Distribution) -> str:
        """Extract and normalize distribution name from metadata.

        Args:
            dist: Distribution object.

        Returns:
            Normalized package name (lowercase, underscores).
        """
        # replace - with _ to handle packages like pyrig
        name: str = dist.metadata["Name"]
        return DependencyGraph.normalize_package_name(name)

    @staticmethod
    def get_all_dependencies() -> list[str]:
        """Get all installed package names.

        Returns:
            List of normalized package names.
        """
        dists = importlib.metadata.distributions()
        # extract the name from the metadata
        return [DependencyGraph.parse_distname_from_metadata(dist) for dist in dists]

    @staticmethod
    def normalize_package_name(name: str) -> str:
        """Normalize a package name (lowercase, hyphens → underscores).

        Args:
            name: Package name to normalize.

        Returns:
            Normalized package name.
        """
        return name.lower().replace("-", "_").strip()

    @staticmethod
    def parse_pkg_name_from_req(req: str) -> str | None:
        """Extract package name from a requirement string.

        Uses pre-compiled regex for better performance when parsing many requirements.

        Args:
            req: Requirement string (e.g., "requests>=2.0,<3.0").

        Returns:
            Normalized package name, or None if parsing fails.
        """
        # Split on the first non-alphanumeric character (except -, _, and .)
        # Uses module-level compiled pattern for performance
        dep = PACKAGE_REQ_NAME_SPLIT_PATTERN.split(req.strip(), maxsplit=1)[0].strip()
        return DependencyGraph.normalize_package_name(dep) if dep else None

    def get_all_depending_on(
        self, package: ModuleType | str, *, include_self: bool = False
    ) -> list[ModuleType]:
        """Find all packages that depend on the given package.

        Primary method for discovering packages that extend pyrig's functionality.

        Args:
            package: Package to find dependents of (module or name string).
            include_self: If True, includes the target package in results.

        Returns:
            List of imported module objects for dependent packages.
            Sorted in topological order (dependencies before dependents).

        Raises:
            ValueError: If package not found in dependency graph.

        Note:
            Only returns packages that can be successfully imported.
        """
        # replace - with _ to handle packages like pyrig
        if isinstance(package, ModuleType):
            package = package.__name__
        target = package.lower()
        if target not in self:
            msg = f"""Package '{target}' not found in dependency graph."""
            raise ValueError(msg)

        dependents_set = self.ancestors(target)
        if include_self:
            dependents_set.add(target)

        # Sort in topological order (dependencies before dependents)
        dependents = self.topological_sort_subgraph(dependents_set)

        logger.debug("Found packages depending on %s: %s", package, dependents)

        return self.import_packages(dependents)

    @staticmethod
    def import_packages(names: Iterable[str]) -> list[ModuleType]:
        """Import packages by name, skipping import failures.

        Args:
            names: Package names to import.

        Returns:
            List of successfully imported modules.
        """
        modules: list[ModuleType] = []
        for name in names:
            module = import_module_with_default(name)
            if module is not None:
                modules.append(module)
        return modules


def get_pkg_name_from_project_name(project_name: str) -> str:
    """Convert project name to package name (hyphens → underscores).

    Args:
        project_name: Project name.

    Returns:
        Package name.
    """
    return project_name.replace("-", "_")


def get_project_name_from_pkg_name(pkg_name: str) -> str:
    """Convert package name to project name (underscores → hyphens).

    Args:
        pkg_name: Package name.

    Returns:
        Project name.
    """
    return pkg_name.replace("_", "-")


def get_project_name_from_cwd() -> str:
    """Get project name from current directory name.

    Returns:
        Current directory name.
    """
    cwd = Path.cwd()
    return cwd.name


def get_pkg_name_from_cwd() -> str:
    """Get package name from current directory name.

    Returns:
        Package name (directory name with underscores).
    """
    return get_pkg_name_from_project_name(get_project_name_from_cwd())


def get_objs_from_obj(
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
            return get_modules_and_packages_from_package(obj)[1]
        objs: list[Callable[..., Any] | type] = []
        objs.extend(get_all_functions_from_module(obj))
        objs.extend(get_all_cls_from_module(obj))
        return objs
    if isinstance(obj, type):
        return get_all_methods_from_cls(obj, exclude_parent_methods=True)
    return []


@cache
def discover_equivalent_modules_across_dependents(
    module: ModuleType, dep: ModuleType, until_pkg: ModuleType | None = None
) -> list[ModuleType]:
    """Find equivalent module paths across all packages that depend on a dependency.

    Core function for pyrig's multi-package architecture. Given a module path
    within a base dependency (e.g., ``pyrig.dev.configs``), discovers and imports
    the equivalent module path in every package that depends on that dependency
    (e.g., ``myapp.dev.configs``, ``other_pkg.dev.configs``).

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
            For example, ``pyrig.dev.configs`` would find ``myapp.dev.configs``
            in a package ``myapp`` that depends on ``pyrig``.
        dep: The base dependency package. All packages depending on this will
            be searched for equivalent modules.
        until_pkg: Optional package to stop at. When provided, stops iterating
            through dependents once this package is reached (inclusive).
            Useful for limiting discovery scope.

    Returns:
        List of imported module objects from all dependent packages, in
        topological order (base dependency first, then dependents in order).

    Example:
        >>> # Find all dev.configs modules across pyrig ecosystem
        >>> from pyrig.dev import configs
        >>> import pyrig
        >>> modules = discover_equivalent_modules_across_dependents(configs, pyrig)
        >>> # Returns: [pyrig.dev.configs, myapp.dev.configs, other_pkg.dev.configs]

    Note:
        The module path transformation is a simple string replacement of the
        first occurrence of ``dep.__name__`` with each dependent package name.
        This assumes consistent package structure across the ecosystem.

    See Also:
        DependencyGraph.get_all_depending_on: Finds dependent packages
        discover_subclasses_across_dependents: Uses this to find subclasses
    """
    module_name = module.__name__
    logger.debug(
        "Discovering modules equivalent to %s in packages depending on %s",
        module_name,
        dep.__name__,
    )
    graph = DependencyGraph.cached()
    pkgs = graph.get_all_depending_on(dep, include_self=True)

    modules: list[ModuleType] = []
    for pkg in pkgs:
        pkg_module_name = module_name.replace(dep.__name__, pkg.__name__, 1)
        pkg_module_path = ModulePath.pkg_name_to_relative_dir_path(pkg_module_name)
        pkg_module = import_module_with_file_fallback(pkg_module_path)
        modules.append(pkg_module)
        if isinstance(until_pkg, ModuleType) and pkg.__name__ == until_pkg.__name__:
            break
    logger.debug(
        "Found modules equivalent to %s: %s", module_name, [m.__name__ for m in modules]
    )
    return modules


@cache
def discover_subclasses_across_dependents[T: type](
    cls: T,
    dep: ModuleType,
    load_pkg_before: ModuleType,
    *,
    discard_parents: bool = False,
    exclude_abstract: bool = False,
) -> list[T]:
    """Discover all subclasses of a class across the entire dependency ecosystem.

    Primary discovery function for pyrig's multi-package plugin architecture.
    Combines ``discover_equivalent_modules_across_dependents`` with
    ``get_all_subclasses`` to find subclass implementations across all packages
    that depend on a base dependency.

    This is the main mechanism that enables:
        - ConfigFile subclasses to be discovered across all dependent packages
        - BuilderConfigFile implementations to be found and executed
        - Plugin-style extensibility without explicit registration

    The discovery process:
        1. Finds all equivalent modules across dependent packages using
           ``discover_equivalent_modules_across_dependents``
        2. For each module, calls ``get_all_subclasses`` to discover subclasses
           of ``cls`` defined in that module (applying ``discard_parents`` and
           ``exclude_abstract`` filters per-module)
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
        load_pkg_before: Template module path to replicate across dependents.
            For example, ``pyrig.dev.configs`` would search for subclasses in
            ``myapp.dev.configs`` for each dependent package ``myapp``.
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
        >>> from pyrig.dev import configs
        >>> import pyrig
        >>> subclasses = discover_subclasses_across_dependents(
        ...     cls=ConfigFile,
        ...     dep=pyrig,
        ...     load_pkg_before=configs,
        ...     discard_parents=True,
        ...     exclude_abstract=True,
        ... )
        >>> # Returns: [PyprojectConfigFile, RuffConfigFile, MyAppConfig, ...]

    Note:
        When ``discard_parents=True``, the filtering is performed twice: once
        within each ``get_all_subclasses`` call (per-module) and once after
        aggregation (cross-module). The second pass is essential because a
        parent class from module A and its child from module B would both
        survive the per-module filtering.

    See Also:
        discover_equivalent_modules_across_dependents: Module discovery
        get_all_subclasses: Per-module subclass discovery
        discover_leaf_subclass_across_dependents: When exactly one leaf expected
    """
    logger.debug(
        "Discovering subclasses of %s from modules in packages depending on %s",
        cls.__name__,
        dep.__name__,
    )
    subclasses: list[T] = []
    for pkg in discover_equivalent_modules_across_dependents(load_pkg_before, dep):
        subclasses.extend(
            get_all_subclasses(
                cls,
                load_package_before=pkg,
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
    cls: T, dep: ModuleType, load_pkg_before: ModuleType
) -> T:
    """Discover the single deepest subclass in the inheritance hierarchy.

    Specialized discovery function for cases where exactly one "final" subclass
    is expected across the entire dependency ecosystem. Used when a base class
    should have a single active implementation determined by the inheritance
    chain.

    This is typically used by ``ConfigFile.L`` to find the most-derived
    version of a config file class. For example, if:
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
        load_pkg_before: Template module path to replicate across dependents.

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
        ...     load_pkg_before=configs,
        ... )
        >>> # Returns the most-derived PyprojectConfigFile subclass

    Note:
        Abstract classes are NOT excluded - the leaf may be abstract if no
        concrete implementation exists. This is intentional for cases where
        the leaf class defines the interface but concrete instantiation
        happens elsewhere.

    See Also:
        discover_subclasses_across_dependents: General multi-subclass discovery
        ConfigFile.L: Primary use case for this function
    """
    classes = discover_subclasses_across_dependents(
        cls=cls,
        dep=dep,
        load_pkg_before=load_pkg_before,
        discard_parents=True,
        exclude_abstract=False,
    )
    # raise if more than one final leaf
    if len(classes) > 1:
        msg = (
            f"Multiple final leaves found for {cls.__name__} "
            f"in {load_pkg_before.__name__}: {classes}"
        )
        raise ValueError(msg)
    leaf = classes[0]
    logger.debug("Found final leaf of %s: %s", cls.__name__, leaf.__name__)
    return leaf
