"""Package utilities for introspection and manipulation.

This module provides comprehensive utility functions for working with Python packages,
including package discovery, creation, traversal, and module extraction. It handles
both regular packages and namespace packages, offering tools for filesystem operations
and module imports related to package structures.

The utilities support both static package analysis and dynamic package manipulation,
making them suitable for code generation, testing frameworks, and package management.
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
from typing import Any

import networkx as nx
from setuptools import find_namespace_packages as _find_namespace_packages
from setuptools import find_packages as _find_packages

logger = logging.getLogger(__name__)


def get_src_package() -> ModuleType:
    """Identify and return the main source package of the project.

    Discovers the main source package by finding all top-level packages
    and filtering out the test package. This is useful for automatically
    determining the package that contains the actual implementation code.

    Returns:
        The main source package as a module object

    Raises:
        StopIteration: If no source package can be found or
                       if only the test package exists

    """
    from pyrig.src.modules.module import to_path  # noqa: PLC0415
    from pyrig.src.testing.convention import TESTS_PACKAGE_NAME  # noqa: PLC0415

    package_names = find_packages(depth=0, include_namespace_packages=False)
    package_paths = [to_path(p, is_package=True) for p in package_names]
    pkg = next(p for p in package_paths if p.name != TESTS_PACKAGE_NAME)

    return import_pkg_from_path(pkg)


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
    from pyrig.dev.configs.git.gitignore import (  # noqa: PLC0415
        GitIgnoreConfigFile,
    )
    from pyrig.src.modules.module import (  # noqa: PLC0415
        import_module_from_path,
        to_path,
    )

    modules_and_packages = list(
        pkgutil.iter_modules(package.__path__, prefix=package.__name__ + ".")
    )
    packages: list[ModuleType] = []
    modules: list[ModuleType] = []
    for _finder, name, is_pkg in modules_and_packages:
        path = to_path(name, is_package=is_pkg)
        if GitIgnoreConfigFile.path_is_in_gitignore(path):
            continue
        mod = import_module_from_path(path)
        if is_pkg:
            packages.append(mod)
        else:
            modules.append(mod)

    # make consistent order
    packages.sort(key=lambda p: p.__name__)
    modules.sort(key=lambda m: m.__name__)

    return packages, modules


def find_packages(
    *,
    depth: int | None = None,
    include_namespace_packages: bool = False,
    where: str = ".",
    exclude: Iterable[str] | None = None,
    include: Iterable[str] = ("*",),
) -> list[str]:
    """Discover Python packages in the specified directory.

    Finds all Python packages in the given directory, with options to filter
    by depth, include/exclude patterns, and namespace packages. This is a wrapper
    around setuptools' find_packages and find_namespace_packages functions with
    additional filtering capabilities.

    Args:
        depth: Optional maximum depth of package nesting to include (None for unlimited)
        include_namespace_packages: Whether to include namespace packages
        where: Directory to search for packages (default: current directory)
        exclude: Patterns of package names to exclude
        include: Patterns of package names to include

    Returns:
        A list of package names as strings

    Example:
        find_packages(depth=1) might return ["package1", "package2"]

    """
    gitignore_path = Path(".gitignore")
    if exclude is None:
        exclude = (
            gitignore_path.read_text(encoding="utf-8").splitlines()
            if gitignore_path.exists()
            else []
        )
        exclude = [
            p.replace("/", ".").removesuffix(".") for p in exclude if p.endswith("/")
        ]
    if include_namespace_packages:
        package_names = _find_namespace_packages(
            where=where, exclude=exclude, include=include
        )
    else:
        package_names = _find_packages(where=where, exclude=exclude, include=include)

    # Convert to list of strings explicitly
    package_names_list: list[str] = list(map(str, package_names))

    if depth is not None:
        package_names_list = [p for p in package_names_list if p.count(".") <= depth]

    return package_names_list


def find_packages_as_modules(
    *,
    depth: int | None = None,
    include_namespace_packages: bool = False,
    where: str = ".",
    exclude: Iterable[str] | None = None,
    include: Iterable[str] = ("*",),
) -> list[ModuleType]:
    """Discover and import Python packages in the specified directory.

    Similar to find_packages, but imports and returns the actual module objects
    instead of just the package names.

    Args:
        depth: Optional maximum depth of package nesting to include (None for unlimited)
        include_namespace_packages: Whether to include namespace packages
        where: Directory to search for packages (default: current directory)
        exclude: Patterns of package names to exclude
        include: Patterns of package names to include

    Returns:
        A list of imported package module objects

    Note:
        All discovered packages are imported during this process.

    """
    package_names = find_packages(
        depth=depth,
        include_namespace_packages=include_namespace_packages,
        where=where,
        exclude=exclude,
        include=include,
    )
    return [import_module(package_name) for package_name in package_names]


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


class DependencyGraph(nx.DiGraph):  # type: ignore [type-arg]
    """A directed graph representing Python package dependencies."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the dependency graph and build it immediately."""
        super().__init__(*args, **kwargs)
        self.build()

    def build(self) -> None:
        """Build the graph from installed Python distributions."""
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
        """Extract the distribution name from its metadata."""
        # replace - with _ to handle packages like pyrig
        name: str = dist.metadata["Name"]
        return DependencyGraph.normalize_package_name(name)

    @staticmethod
    def normalize_package_name(name: str) -> str:
        """Normalize a package name."""
        return name.lower().replace("-", "_").strip()

    @staticmethod
    def parse_pkg_name_from_req(req: str) -> str | None:
        """Extract the bare dependency name from a requirement string."""
        # split on the first non alphanumeric character like >, <, =, etc.
        # keep - and _ for names like pyrig or pyrig
        dep = re.split(r"[^a-zA-Z0-9_-]", req.strip())[0].strip()
        return DependencyGraph.normalize_package_name(dep) if dep else None

    def get_all_depending_on(
        self, package: ModuleType | str, *, include_self: bool = False
    ) -> list[ModuleType]:
        """Return all packages that directly or indirectly depend on the given package.

        Args:
            package: The module whose dependents should be found.
            include_self: Whether to include the package itself in the result.

        Returns:
            A list of imported module objects representing dependents.
            Order is that the the one that has the most deps is last and the one that
            has the least deps is first.
        """
        # replace - with _ to handle packages like pyrig
        if isinstance(package, ModuleType):
            package = package.__name__
        target = package.lower()
        if target not in self:
            msg = f"""Package '{target}' not found in dependency graph.
Possibly the target is the current project itself."""
            logger.warning(msg)
            return []

        dependents: list[str] = list(nx.ancestors(self, target))
        if include_self:
            dependents.insert(0, target)

        # sort by number of dependencies
        dependents = sorted(dependents, key=lambda p: len(self[p]), reverse=True)

        return self.import_packages(dependents)

    @staticmethod
    def import_packages(names: Iterable[str]) -> list[ModuleType]:
        """Attempt to import all module names that can be resolved."""
        modules: list[ModuleType] = []
        for name in names:
            spec = importlib.util.find_spec(name)
            if spec is not None:
                modules.append(importlib.import_module(name))
        return modules


def import_pkg_from_path(package_dir: Path) -> ModuleType:
    """Import a package from a path."""
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
