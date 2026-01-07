"""Package discovery utilities.

Utilities for discovering Python packages with additional filtering and automatic
.gitignore integration to exclude virtual environments and build directories.

Functions:
    find_packages: Discover Python packages with depth and pattern filtering
    src_pkg_is_pyrig: Check if the current project is pyrig itself
    get_namespace_packages: Find all PEP 420 namespace packages

Examples:
    Find packages with depth limit::

        >>> from pyrig.dev.utils.packages import find_packages
        >>> find_packages(depth=0)
        ['myproject', 'tests']

    Check if current project is pyrig::

        >>> from pyrig.dev.utils.packages import src_pkg_is_pyrig
        >>> src_pkg_is_pyrig()
        False

See Also:
    setuptools.find_packages: Underlying package discovery function
    setuptools.find_namespace_packages: PEP 420 namespace package discovery
"""

import logging
from collections.abc import Iterable
from pathlib import Path

from setuptools import find_namespace_packages as _find_namespace_packages
from setuptools import find_packages as _find_packages

import pyrig
from pyrig.dev.management.docs_builder import DocsBuilder
from pyrig.dev.utils.version_control import path_is_in_ignore
from pyrig.src.modules.path import ModulePath

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
        p
        for p in namespace_packages
        if not p.startswith(DocsBuilder.L.get_docs_dir().name)
    ]
    # exclude all that are in .gitignore
    namespace_packages = [
        p
        for p in namespace_packages
        if not path_is_in_ignore(ModulePath.pkg_name_to_relative_dir_path(p))
    ]
    result = list(set(namespace_packages) - set(packages))
    logger.debug("Found %d namespace packages: %s", len(result), result)
    return result
