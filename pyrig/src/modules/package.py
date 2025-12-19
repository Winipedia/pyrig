"""Package discovery, traversal, and dependency graph analysis.

This module provides utilities for working with Python packages, including
package discovery, recursive traversal, and dependency graph analysis. The
`DependencyGraph` class is central to pyrig's multi-package architecture,
enabling automatic discovery of all packages that depend on pyrig.

Key capabilities:
    - Package discovery: Find packages in a directory with depth filtering
    - Package traversal: Walk through package hierarchies recursively
    - Dependency analysis: Build and query the installed package dependency graph
    - Package copying: Duplicate package structures for scaffolding

The dependency graph enables pyrig to find all packages that depend on it,
then discover ConfigFile implementations, Builder subclasses, and other
extensible components in those packages.

Example:
    >>> from pyrig.src.modules.package import DependencyGraph
    >>> graph = DependencyGraph()
    >>> dependents = graph.get_all_depending_on("pyrig")
    >>> [m.__name__ for m in dependents]
    ['myapp', 'other_pkg']
"""

import importlib.machinery
import importlib.metadata
import importlib.util
import logging
import pkgutil
import re
from collections.abc import Callable, Generator, Iterable, Sequence
from pathlib import Path
from types import ModuleType
from typing import Any

from pyrig.src.graph import DiGraph
from pyrig.src.modules.class_ import get_all_cls_from_module, get_all_methods_from_cls
from pyrig.src.modules.function import get_all_functions_from_module
from pyrig.src.modules.module import (
    import_module_with_default,
    import_module_with_file_fallback,
)
from pyrig.src.modules.path import ModulePath, make_dir_with_init_file

logger = logging.getLogger(__name__)

DOCS_DIR_NAME = "docs"


def module_is_package(obj: ModuleType) -> bool:
    """Determine if a module object represents a package.

    Checks if the given module object is a package by looking for the __path__
    attribute, which is only present in package modules.

    Args:
        obj: The module object to check

    Returns:
        True if the module is a package, False otherwise

    Note:
        This works for both regular packages and namespace packages.

    """
    return hasattr(obj, "__path__")


def get_modules_and_packages_from_package(
    package: ModuleType,
) -> tuple[list[ModuleType], list[ModuleType]]:
    """Extract all direct subpackages and modules from a package.

    Discovers and imports all direct child modules and subpackages within
    the given package. Returns them as separate lists.

    Args:
        package: The package module to extract subpackages and modules from

    Returns:
        A tuple containing (list of subpackages, list of modules)

    Note:
        Only includes direct children, not recursive descendants.
        All discovered modules and packages are imported during this process.

    """
    from pyrig.src.modules.module import (  # noqa: PLC0415
        import_module_with_file_fallback,
    )

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
    """Recursively walk through a package and all its subpackages.

    Performs a depth-first traversal of the package hierarchy, yielding each
    package along with its direct module children.

    Args:
        package: The root package module to start walking from

    Yields:
        Tuples of (package, list of modules in package)

    Note:
        All packages and modules are imported during this process.
        The traversal is depth-first, so subpackages are fully processed
        before moving to siblings.

    """
    subpackages, submodules = get_modules_and_packages_from_package(package)
    yield package, submodules
    for subpackage in subpackages:
        yield from walk_package(subpackage)


def create_package(path: Path) -> ModuleType:
    """Create a package at the given path.

    The given patz must not end with __init__.py.

    Args:
        path: The dir path to create the package at

    """
    if path == Path.cwd():
        msg = f"Cannot create package {path=} because it is the CWD"
        raise ValueError(msg)
    make_dir_with_init_file(path)

    return import_pkg_with_dir_fallback(path)


def import_pkg_with_dir_fallback(path: Path) -> ModuleType:
    """Import a package from a path.

    If pkg cannot be found via normal importlib, try to import from path.

    Args:
        path (Path): The path to the package

    Returns:
        ModuleType: The imported package module.
    """
    path = path.resolve()
    module_name = ModulePath.absolute_path_to_module_name(path)
    pkg = import_module_with_default(module_name)
    if isinstance(pkg, ModuleType):
        return pkg
    return import_pkg_from_dir(path)


class DependencyGraph(DiGraph):
    """A directed graph of installed Python package dependencies.

    Builds a graph where nodes are package names and edges represent
    dependency relationships (package -> dependency). This enables
    finding all packages that depend on a given package, which is
    central to pyrig's multi-package discovery system.

    The graph is built automatically on instantiation by scanning all
    installed distributions via `importlib.metadata`.

    Attributes:
        Inherits all attributes from DiGraph.

    Example:
        >>> graph = DependencyGraph()
        >>> # Find all packages that depend on pyrig
        >>> dependents = graph.get_all_depending_on("pyrig")
        >>> [m.__name__ for m in dependents]
        ['myapp', 'other_pkg']
    """

    def __init__(self) -> None:
        """Initialize and build the dependency graph.

        Scans all installed Python distributions and builds the dependency
        graph immediately. Package names are normalized (lowercase, hyphens
        replaced with underscores).
        """
        super().__init__()
        self.build()

    def build(self) -> None:
        """Build the graph from installed Python distributions.

        Iterates through all installed distributions, adding each as a node
        and creating edges from each package to its dependencies.
        """
        for dist in importlib.metadata.distributions():
            name = self.parse_distname_from_metadata(dist)
            self.add_node(name)

            requires = dist.requires or []
            for req in requires:
                dep = self.parse_pkg_name_from_req(req)
                if dep:
                    self.add_edge(name, dep)  # package → dependency

    @staticmethod
    def parse_distname_from_metadata(dist: importlib.metadata.Distribution) -> str:
        """Extract and normalize the distribution name from metadata.

        Args:
            dist: A distribution object from importlib.metadata.

        Returns:
            The normalized package name (lowercase, underscores).
        """
        # replace - with _ to handle packages like pyrig
        name: str = dist.metadata["Name"]
        return DependencyGraph.normalize_package_name(name)

    @staticmethod
    def get_all_dependencies() -> list[str]:
        """Get all installed package names.

        Returns:
            A list of all installed package names, normalized.
        """
        dists = importlib.metadata.distributions()
        # extract the name from the metadata
        return [DependencyGraph.parse_distname_from_metadata(dist) for dist in dists]

    @staticmethod
    def normalize_package_name(name: str) -> str:
        """Normalize a package name for consistent comparison.

        Converts to lowercase and replaces hyphens with underscores,
        matching Python's import name conventions.

        Args:
            name: The package name to normalize.

        Returns:
            The normalized package name.
        """
        return name.lower().replace("-", "_").strip()

    @staticmethod
    def parse_pkg_name_from_req(req: str) -> str | None:
        """Extract the bare package name from a requirement string.

        Parses requirement strings like "requests>=2.0" or "numpy[extra]"
        to extract just the package name.

        Args:
            req: A requirement string (e.g., "requests>=2.0,<3.0").

        Returns:
            The normalized package name, or None if parsing fails.
        """
        # split on the first non alphanumeric character like >, <, =, etc.
        # keep - and _ for names like pyrig or pyrig
        dep = re.split(r"[^a-zA-Z0-9_-]", req.strip())[0].strip()
        return DependencyGraph.normalize_package_name(dep) if dep else None

    def get_all_depending_on(
        self, package: ModuleType | str, *, include_self: bool = False
    ) -> list[ModuleType]:
        """Find all packages that depend on the given package.

        Traverses the dependency graph to find all packages that directly
        or indirectly depend on the specified package. Results are sorted
        in topological order (dependencies before dependents).

        This is the primary method used by pyrig to discover all packages
        in the ecosystem that extend pyrig's functionality.

        Args:
            package: The package to find dependents of. Can be a module
                object or a package name string.
            include_self: If True, includes the target package itself
                in the results.

        Returns:
            A list of imported module objects for all dependent packages.
            Sorted in topological order so dependencies come before dependents.
            For example: [pyrig, pkg1, pkg2] where pkg1 depends on pyrig and
            pkg2 depends on pkg1.

        Note:
            Only returns packages that can be successfully imported.
            Logs a warning if the target package is not in the graph.
        """
        # replace - with _ to handle packages like pyrig
        if isinstance(package, ModuleType):
            package = package.__name__
        target = package.lower()
        if target not in self:
            msg = f"""Package '{target}' not found in dependency graph."""
            logger.warning(msg)
            return []

        dependents_set = self.ancestors(target)
        if include_self:
            dependents_set.add(target)

        # Sort in topological order (dependencies before dependents)
        dependents = self.topological_sort_subgraph(dependents_set)

        return self.import_packages(dependents)

    @staticmethod
    def import_packages(names: Iterable[str]) -> list[ModuleType]:
        """Import packages by name, skipping those that cannot be imported.

        Args:
            names: Package names to import.

        Returns:
            A list of successfully imported module objects.
        """
        from pyrig.src.modules.module import import_module_with_default  # noqa: PLC0415

        modules: list[ModuleType] = []
        for name in names:
            module = import_module_with_default(name)
            if module is not None:
                modules.append(module)
        return modules


def import_pkg_from_dir(package_dir: Path) -> ModuleType:
    """Import a package from a directory.

    This function imports a package from a directory by creating a module
    spec and loading the module from the __init__.py file in the directory.

    Args:
        package_dir (Path): The directory containing the package to import.

    Raises:
        ValueError: If the package directory does not contain an __init__.py file.

    Returns:
        ModuleType: The imported package module.
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


def get_pkg_name_from_project_name(project_name: str) -> str:
    """Convert a project name to a package name.

    Args:
        project_name: Project name with hyphens.

    Returns:
        Package name with underscores.
    """
    return project_name.replace("-", "_")


def get_project_name_from_pkg_name(pkg_name: str) -> str:
    """Convert a package name to a project name.

    Args:
        pkg_name: Package name with underscores.

    Returns:
        Project name with hyphens.
    """
    return pkg_name.replace("_", "-")


def get_project_name_from_cwd() -> str:
    """Derive the project name from the current directory.

    The project name is assumed to match the directory name.

    Returns:
        The current directory name.
    """
    cwd = Path.cwd()
    return cwd.name


def get_pkg_name_from_cwd() -> str:
    """Derive the package name from the current directory.

    Returns:
        The package name (directory name with hyphens as underscores).
    """
    return get_pkg_name_from_project_name(get_project_name_from_cwd())


def get_objs_from_obj(
    obj: Callable[..., Any] | type | ModuleType,
) -> Sequence[Callable[..., Any] | type | ModuleType]:
    """Extract all contained objects from a container object.

    Retrieves all relevant objects contained within the given object, with behavior
    depending on the type of the container:
    - For modules: returns all functions and classes defined in the module
    - For packages: returns all submodules in the package
    - For classes: returns all methods defined directly in the class
    - For other objects: returns an empty list

    Args:
        obj: The container object to extract contained objects from

    Returns:
        A sequence of objects contained within the given container object

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

    This is a key function for pyrig's multi-package architecture. Given a
    module path within a dependency (e.g.,  smth.dev.configs`), it finds
    the equivalent module path in all packages that depend on that dependency
    (e.g., `myapp.dev.configs`, `other_pkg.dev.configs`).

    This enables automatic discovery of ConfigFile implementations, Builder
    subclasses, and other extensible components across the entire ecosystem
    of packages that depend on pyrig.

    Args:
        module: The module to use as a template (e.g., `smth.dev.configs`).
        dep: The dependency package that other packages depend on (e.g., pyrig or smth).
        until_pkg: Optional package to stop at. If provided, only modules from
            packages that depend on `until_pkg` will be returned.

    Returns:
        A list of equivalent modules from all packages that depend on `dep`,
        including the original module itself.

    Example:
        >>> import smth
        >>> from smth.dev import configs
        >>> modules = get_same_modules_from_deps_depen_on_dep(
        ...     configs, smth
        ... )
        >>> [m.__name__ for m in modules]
        ['smth.dev.configs', 'myapp.dev.configs', 'other_pkg.dev.configs']
    """
    module_name = module.__name__
    graph = DependencyGraph()
    pkgs = graph.get_all_depending_on(dep, include_self=True)

    modules: list[ModuleType] = []
    for pkg in pkgs:
        pkg_module_name = module_name.replace(dep.__name__, pkg.__name__, 1)
        pkg_module_path = ModulePath.pkg_name_to_relative_dir_path(pkg_module_name)
        pkg_module = import_module_with_file_fallback(pkg_module_path)
        modules.append(pkg_module)
        if isinstance(until_pkg, ModuleType) and pkg.__name__ == until_pkg.__name__:
            break
    return modules
