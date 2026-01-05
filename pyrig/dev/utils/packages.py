"""Package discovery and source package identification utilities.

Utilities for discovering Python packages and identifying the main source package.
Wraps setuptools' package discovery with additional filtering and automatic
.gitignore integration to exclude virtual environments and build directories.

Functions:
    find_packages: Discover Python packages with depth and pattern filtering
    get_src_package: Identify and import the main source package
    src_pkg_is_pyrig: Check if the current project is pyrig itself
    get_namespace_packages: Find all PEP 420 namespace packages

Examples:
    Discover the main source package::

        >>> from pyrig.dev.utils.packages import get_src_package
        >>> pkg = get_src_package()
        >>> print(pkg.__name__)
        myproject

    Find packages with depth limit::

        >>> from pyrig.dev.utils.packages import find_packages
        >>> find_packages(depth=0)
        ['myproject', 'tests']

See Also:
    setuptools.find_packages: Underlying package discovery function
    setuptools.find_namespace_packages: PEP 420 namespace package discovery
"""

import logging
from collections.abc import Iterable
from importlib import import_module
from pathlib import Path
from types import ModuleType

from setuptools import find_namespace_packages as _find_namespace_packages
from setuptools import find_packages as _find_packages

import pyrig
from pyrig.dev.utils.version_control import load_gitignore, path_is_in_gitignore_lines
from pyrig.src.modules.package import DOCS_DIR_NAME
from pyrig.src.modules.path import ModulePath
from pyrig.src.testing.convention import TESTS_PACKAGE_NAME

logger = logging.getLogger(__name__)


def find_packages(
    *,
    depth: int | None = None,
    include_namespace_packages: bool = False,
    where: str = ".",
    exclude: Iterable[str] | None = None,
    include: Iterable[str] = ("*",),
) -> list[str]:
    """Discover Python packages in the specified directory.

    Wraps setuptools' package discovery with additional filtering. Automatically
    excludes packages listed in .gitignore to prevent discovering packages in
    virtual environments and build directories.

    Args:
        depth: Maximum package nesting depth. Examples:
            - depth=0: Only top-level packages ("myproject", "tests")
            - depth=1: Top-level plus one level ("myproject.utils")
            - None: Unlimited depth (all nested packages)
        include_namespace_packages: If True, includes PEP 420 namespace packages
            (without `__init__.py`). If False, only regular packages.
        where: Root directory to search. Defaults to current directory (".").
        exclude: Glob patterns for package names to exclude. If None, automatically
            reads .gitignore and converts directory patterns to package patterns
            (e.g., "build/" becomes "build").
        include: Glob patterns for package names to include. Defaults to all ("*").

    Returns:
        List of discovered package names as dot-separated strings. Returns empty
        list if no packages found.

    Examples:
        Find only top-level packages::

            >>> find_packages(depth=0)
            ['myproject', 'tests']

        Find all packages including namespace packages::

            >>> find_packages(include_namespace_packages=True)
            ['myproject', 'myproject.utils', 'myproject.core']

        Find packages excluding tests::

            >>> find_packages(exclude=['tests*'])
            ['myproject', 'myproject.utils']
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


def get_src_package() -> ModuleType:
    """Identify and import the main source package of the project.

    Discovers the main source package by finding all top-level packages and
    filtering out the tests package. Assumes a standard Python project structure
    with exactly one non-test top-level package.

    Returns:
        The main source package as an imported module object with access to all
        module attributes (__name__, __file__, __version__, etc.).

    Raises:
        ModuleNotFoundError: If the source package cannot be reliably determined
            (zero or multiple non-test top-level packages, or import failure).

    Examples:
        Get the source package::

            >>> pkg = get_src_package()
            >>> print(pkg.__name__)
            myproject

        Access package contents::

            >>> pkg = get_src_package()
            >>> from importlib import import_module
            >>> core = import_module(f"{pkg.__name__}.core")

    Note:
        Only considers regular packages (with __init__.py), not namespace packages.
    """
    logger.debug("Discovering top-level source package")
    package_names = find_packages(depth=0, include_namespace_packages=False)
    package_paths = [ModulePath.pkg_name_to_relative_dir_path(p) for p in package_names]
    pkgs = [p for p in package_paths if p.name not in {TESTS_PACKAGE_NAME}]
    if len(pkgs) != 1:
        msg = "Could not reliably determine source package."
        raise ModuleNotFoundError(msg)
    pkg = pkgs[0]
    pkg_name = pkg.name
    logger.debug("Identified source package: %s", pkg_name)

    return import_module(pkg_name)


def src_pkg_is_pyrig() -> bool:
    """Check if the current project is pyrig itself.

    Determines whether the current working directory is the pyrig project by
    checking if "pyrig" is among the top-level packages.

    Returns:
        True if "pyrig" is a top-level package in the current directory.

    Examples:
        Conditional logic for pyrig development::

            >>> if src_pkg_is_pyrig():
            ...     print("Running in pyrig development mode")

    Note:
        Detects the pyrig repository, not pyrig as an installed dependency.
    """
    pkgs = find_packages(depth=0, include_namespace_packages=False)
    return pyrig.__name__ in pkgs


def get_namespace_packages() -> list[str]:
    """Find all PEP 420 namespace packages in the project.

    Discovers namespace packages (packages without `__init__.py`) by comparing
    results from find_namespace_packages with find_packages. Automatically excludes
    docs directory and .gitignore patterns.

    Returns:
        List of namespace package names as dot-separated strings. Empty list if
        none found.

    Examples:
        Find all namespace packages::

            >>> ns_pkgs = get_namespace_packages()
            >>> print(ns_pkgs)
            ['myproject.plugins', 'myproject.extensions']

    See Also:
        PEP 420: Implicit Namespace Packages
    """
    logger.debug("Discovering namespace packages")
    packages = find_packages(depth=None)
    namespace_packages = find_packages(depth=None, include_namespace_packages=True)
    namespace_packages = [
        p for p in namespace_packages if not p.startswith(DOCS_DIR_NAME)
    ]
    # exclude all that are in .gitignore
    gitignore_lines = load_gitignore()
    namespace_packages = [
        p
        for p in namespace_packages
        if not path_is_in_gitignore_lines(gitignore_lines, p)
    ]
    result = list(set(namespace_packages) - set(packages))
    logger.debug("Found %d namespace packages: %s", len(result), result)
    return result
