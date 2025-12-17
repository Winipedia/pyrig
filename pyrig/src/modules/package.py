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
import shutil
import sys
from collections.abc import Generator, Iterable
from importlib import import_module
from pathlib import Path
from types import ModuleType

from pyrig.src.graph import DiGraph

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
        import_module_from_file,
        to_path,
    )

    modules_and_packages = list(
        pkgutil.iter_modules(package.__path__, prefix=package.__name__ + ".")
    )
    packages: list[ModuleType] = []
    modules: list[ModuleType] = []
    for _finder, name, is_pkg in modules_and_packages:
        path = to_path(name, is_package=is_pkg)

        mod = import_module_from_file(path)
        if is_pkg:
            packages.append(mod)
        else:
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


def copy_package(
    src_package: ModuleType,
    dst: str | Path | ModuleType,
    *,
    with_file_content: bool = True,
    skip_existing: bool = True,
) -> None:
    """Copy a package to a different destination.

    Takes a ModuleType of package and a destination package name and then copies
    the package to the destination. If with_file_content is True, it copies the
    content of the files, otherwise it just creates the files.

    Args:
        src_package (ModuleType): The package to copy
        dst (str | Path): destination package name as a
                          Path with / or as a str with dots
        with_file_content (bool, optional): copies the content of the files.
        skip_existing (bool, optional): skips existing files.

    """
    from pyrig.src.modules.module import create_module, to_path  # noqa: PLC0415

    # copy the folder with shutil
    src_path = Path(src_package.__path__[0])
    dst_path = to_path(dst, is_package=True)
    # walk thze src_path and copy the files to dst_path if they do not exist
    for src in src_path.rglob("*"):
        dst_ = dst_path / src.relative_to(src_path)
        if skip_existing and dst_.exists():
            continue
        if src.is_dir():
            dst_.mkdir(parents=True, exist_ok=True)
            continue
        # Ensure parent directory exists before copying file
        dst_.parent.mkdir(parents=True, exist_ok=True)
        if with_file_content:
            shutil.copy2(src, dst_)
        else:
            create_module(dst_, is_package=False)


def get_main_package() -> ModuleType:
    """Gets the main package of the executing code.

    Even when this package is installed as a module.
    """
    from pyrig.src.modules.module import (  # noqa: PLC0415  # avoid circular import
        to_module_name,
    )

    main = sys.modules.get("__main__")
    if main is None:
        msg = "No __main__ module found"
        raise ValueError(msg)

    package_name = getattr(main, "__package__", None)
    if package_name:
        package_name = package_name.split(".")[0]
        return import_module(package_name)

    file_name = getattr(main, "__file__", None)
    if file_name:
        package_name = to_module_name(file_name)
        package_name = package_name.split(".")[0]
        return import_module(package_name)

    msg = "Not able to determine the main package"
    raise ValueError(msg)


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


def import_pkg_from_path(package_dir: Path) -> ModuleType:
    """Import a package from a filesystem path.

    Uses importlib machinery to load a package from its directory path,
    rather than by its module name. Useful when the package is not yet
    in sys.path or when you have a path but not the module name.

    Args:
        package_dir: Path to the package directory (must contain __init__.py).

    Returns:
        The imported package module.

    Raises:
        ValueError: If a module spec cannot be created for the path.
    """
    from pyrig.src.modules.module import to_module_name  # noqa: PLC0415

    package_name = to_module_name(package_dir.resolve().relative_to(Path.cwd()))
    loader = importlib.machinery.SourceFileLoader(
        package_name, str(package_dir / "__init__.py")
    )
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
