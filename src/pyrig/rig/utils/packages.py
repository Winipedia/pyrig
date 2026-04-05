"""Package discovery utilities.

Utilities for discovering Python packages with additional filtering and automatic
.gitignore integration to exclude virtual environments and build directories.

Functions:
    find_packages: Discover Python packages with depth and pattern filtering
    src_package_is_pyrig: Check if the current project is pyrig itself
    find_namespace_packages: Find all PEP 420 namespace packages

Examples:
    Find packages with depth limit:

        >>> from pyrig.rig.utils.packages import find_packages
        >>> find_packages(depth=0)
        ['myproject', 'tests']

    Check if current project is pyrig:

        >>> from pyrig.rig.utils.packages import src_package_is_pyrig
        >>> src_package_is_pyrig()
        False

See Also:
    setuptools.find_packages: Underlying package discovery function
    setuptools.find_namespace_packages: PEP 420 namespace package discovery
"""

import logging
from collections.abc import Generator
from functools import cache
from types import ModuleType

from setuptools import find_namespace_packages as _find_namespace_packages
from setuptools import find_packages as _find_packages

import pyrig
from pyrig.core.iterate import combine_generators
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.project_tester import ProjectTester

logger = logging.getLogger(__name__)


def src_package_is_pyrig() -> bool:
    """Check if the current project is pyrig itself.

    Determines whether the current working directory is the pyrig project by
    checking if "pyrig" is among the top-level packages.

    Returns:
        True if "pyrig" is a top-level package in the current directory.

    Examples:
        Conditional logic for pyrig development:

            >>> if src_package_is_pyrig():
            ...     print("Running in pyrig development mode")

    Note:
        Detects the pyrig repository, not pyrig as an installed dependency.
    """
    return src_package_is_package(pyrig)


@cache
def src_package_is_package(package: ModuleType) -> bool:
    """Check if the given module is the src package of the current project.

    Args:
        package: The module to check.

    Returns:
        True if the module's name matches the top-level package of the current project.
    """
    return (PackageManager.I.source_root() / package.__name__).exists()


def find_packages(
    *,
    depth: int | None = None,
    include_namespace_packages: bool = False,
) -> Generator[str, None, None]:
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
        Find only top-level packages:

            >>> find_packages(depth=0)
            ['myproject', 'tests']

        Find all packages including namespace packages:

            >>> find_packages(include_namespace_packages=True)
            ['myproject', 'myproject.utils', 'myproject.core']

        Find packages excluding tests:

            >>> find_packages(exclude=['tests*'])
            ['myproject', 'myproject.utils']
    """
    find_func = (
        _find_namespace_packages if include_namespace_packages else _find_packages
    )

    tests_package_names = find_func(
        where=".",
        include=(f"{ProjectTester.I.tests_package_name()}*",),
    )
    source_package_names = find_func(
        where=PackageManager.I.source_root(),
    )

    package_names = combine_generators(tests_package_names, source_package_names)
    if depth is not None:
        package_names = (p for p in package_names if p.count(".") <= depth)

    return package_names


def find_namespace_packages() -> Generator[str, None, None]:
    """Find all PEP 420 namespace packages in the project.

    Discovers namespace packages (packages without `__init__.py`) by comparing
    results from find_namespace_packages with find_packages. Automatically excludes
    docs directory and .gitignore patterns.

    Returns:
        Generator of namespace package names as dot-separated strings.
        Empty generator if none found.

    Examples:
        Find all namespace packages:

            >>> ns_packages = find_namespace_packages()
            >>> print(ns_packages)
            ['myproject.plugins', 'myproject.extensions']

    See Also:
        PEP 420: Implicit Namespace Packages
    """
    logger.debug("Discovering namespace packages")
    namespace_packages = find_packages(
        depth=None,
        include_namespace_packages=True,
    )

    packages = set(find_packages(depth=None))
    return (p for p in namespace_packages if p not in packages)
