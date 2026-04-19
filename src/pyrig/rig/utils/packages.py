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

from setuptools import find_namespace_packages as _find_namespace_packages
from setuptools import find_packages as _find_packages

from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.project_tester import ProjectTester

logger = logging.getLogger(__name__)


def find_packages(
    *,
    include_namespace_packages: bool = False,
) -> tuple[str, ...]:
    """Discover Python packages in the specified directory.

    Wraps setuptools' package discovery with additional filtering. Automatically
    excludes packages listed in .gitignore to prevent discovering packages in
    virtual environments and build directories.

    Args:
        include_namespace_packages: If True, includes PEP 420 namespace packages
            (without `__init__.py`). If False, only regular packages.

    Returns:
        Tuple of discovered package names as dot-separated strings. Returns empty
        tuple if no packages found.
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

    return (*tests_package_names, *source_package_names)


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
        include_namespace_packages=True,
    )

    packages = set(find_packages())
    return (p for p in namespace_packages if p not in packages)
