"""Package discovery, traversal, and dependency graph analysis.

Provides utilities for package discovery, recursive traversal, and dependency graph
analysis. The `DependencyGraph` class enables automatic discovery of all packages
that depend on pyrig, allowing discovery of ConfigFile implementations and Builder
subclasses across the ecosystem.
"""

import importlib.metadata
import logging
import re
from collections.abc import Callable, Iterable, Sequence
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

DOCS_DIR_NAME = "docs"

# Pre-compiled regex for parsing package names from requirement strings.
# Matches everything before the first version specifier (>, <, =, [, ;, etc.)
# Allows alphanumeric, underscore, hyphen, and period (for namespace packages).
# Performance: compiled once at module load vs. per-call compilation.
# Used by DependencyGraph and PyprojectConfigFile.
PACKAGE_REQ_NAME_SPLIT_PATTERN = re.compile(r"[^a-zA-Z0-9_.-]")


def create_package(path: Path) -> ModuleType:
    """Create a package at the given path.

    Args:
        path: Directory path (must not end with __init__.py).

    Returns:
        Created package module.

    Raises:
        ValueError: If path is the CWD.
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
    - Packages: all submodules
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


def get_same_modules_from_deps_depen_on_dep(
    module: ModuleType, dep: ModuleType, until_pkg: ModuleType | None = None
) -> list[ModuleType]:
    """Find equivalent modules across all packages depending on a dependency.

    Key function for multi-package architecture. Given a module path within a dependency
    (e.g., `smth.dev.configs`), finds the equivalent path in all packages that depend on
    that dependency (e.g., `myapp.dev.configs`, `other_pkg.dev.configs`).

    Enables automatic discovery of ConfigFile implementations and Builder subclasses
    across the ecosystem.

    Args:
        module: Module to use as template (e.g., `smth.dev.configs`).
        dep: Dependency package (e.g., pyrig or smth).
        until_pkg: Optional package to stop at.

    Returns:
        List of equivalent modules from all packages depending on `dep`.
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


def get_all_subcls_from_mod_in_all_deps_depen_on_dep[T: type](
    cls: T,
    dep: ModuleType,
    load_package_before: ModuleType,
    *,
    discard_parents: bool = False,
    exclude_abstract: bool = False,
) -> list[T]:
    """Find non-abstract subclasses across all packages depending on a dependency.

    Core discovery function for multi-package architecture. Finds all packages depending
    on `dep`, looks for the same relative module path as `load_package_before` in each,
    and discovers subclasses of `cls` in those modules.

    Args:
        cls: Base class to find subclasses of.
        dep: Dependency package (e.g., pyrig or smth).
        load_package_before: Module path within `dep` to use as template.
        discard_parents: If True, keeps only leaf classes.
        exclude_abstract: If True, excludes abstract classes.

    Returns:
        List of discovered non-abstract subclasses.
    """
    logger.debug(
        "Discovering subclasses of %s from modules in packages depending on %s",
        cls.__name__,
        dep.__name__,
    )
    subclasses: list[T] = []
    for pkg in get_same_modules_from_deps_depen_on_dep(load_package_before, dep):
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
