"""Package discovery and source package identification utilities.

This module provides utilities for discovering Python packages in a project
and identifying the main source package. It wraps setuptools' package
discovery functions with additional filtering capabilities and integrates
with pyrig's conventions for test and documentation directories.

Key Functions:
    - `find_packages`: Discover packages with depth and pattern filtering
    - `get_src_package`: Identify the main source package of the project
    - `src_pkg_is_pyrig`: Check if the current project is pyrig itself
    - `get_namespace_packages`: Find all namespace packages in the project

Example:
    >>> from pyrig.dev.utils.packages import get_src_package
    >>> src_pkg = get_src_package()
    >>> print(src_pkg.__name__)
    'myproject'
"""

import logging
from collections.abc import Iterable
from importlib import import_module
from pathlib import Path
from types import ModuleType

from setuptools import find_namespace_packages as _find_namespace_packages
from setuptools import find_packages as _find_packages

import pyrig
from pyrig.dev.utils.git import path_is_in_gitignore
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

    Finds all Python packages in the given directory, with options to filter
    by depth, include/exclude patterns, and namespace packages. This is a wrapper
    around setuptools' `find_packages` and `find_namespace_packages` functions with
    additional filtering capabilities.

    By default, packages listed in `.gitignore` are automatically excluded to avoid
    discovering packages in virtual environments, build directories, etc.

    Args:
        depth: Maximum depth of package nesting to include. For example, depth=0
            returns only top-level packages, depth=1 includes one level of
            subpackages. None means unlimited depth.
        include_namespace_packages: If True, includes PEP 420 namespace packages
            (packages without `__init__.py` files).
        where: Root directory to search for packages. Defaults to current directory.
        exclude: Iterable of glob patterns for package names to exclude. If None,
            automatically excludes patterns from `.gitignore`.
        include: Iterable of glob patterns for package names to include. Defaults
            to all packages ("*").

    Returns:
        List of discovered package names as dot-separated strings (e.g.,
        ["mypackage", "mypackage.subpkg"]).

    Example:
        >>> # Find only top-level packages
        >>> find_packages(depth=0)
        ['myproject', 'tests']

        >>> # Find all packages including namespace packages
        >>> find_packages(include_namespace_packages=True)
        ['myproject', 'myproject.utils', 'myproject.core']

        >>> # Find packages excluding tests
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
    """Identify and return the main source package of the project.

    Discovers the main source package by finding all top-level packages
    and filtering out the test package. This is useful for automatically
    determining the package that contains the actual implementation code.

    The function assumes a standard project structure where there is exactly
    one top-level package that is not the tests package. This is the typical
    layout for Python projects:

        project/
        ├── myproject/      # <- This is the source package
        │   ├── __init__.py
        │   └── ...
        └── tests/          # <- Excluded from consideration
            └── ...

    Returns:
        The main source package as an imported module object.

    Raises:
        ModuleNotFoundError: If the source package cannot be reliably determined
            (e.g., if there are zero or multiple non-test top-level packages).

    Example:
        >>> from pyrig.dev.utils.packages import get_src_package
        >>> pkg = get_src_package()
        >>> print(pkg.__name__)
        'myproject'
        >>> print(pkg.__file__)
        '/path/to/project/myproject/__init__.py'
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

    This is useful for conditional logic that should only run when developing
    pyrig itself, such as updating resource files or running pyrig-specific
    tests.

    Returns:
        True if the current project's source package is pyrig, False otherwise.

    Example:
        >>> from pyrig.dev.utils.packages import src_pkg_is_pyrig
        >>> if src_pkg_is_pyrig():
        ...     print("Running in pyrig development mode")
    """
    pkgs = find_packages(depth=0, include_namespace_packages=False)
    return pyrig.__name__ in pkgs


def get_namespace_packages() -> list[str]:
    """Get all namespace packages in the project.

    Namespace packages (PEP 420) are packages without `__init__.py` files.
    This function finds all such packages, excluding those in the docs directory.

    Returns:
        List of namespace package names as dot-separated strings.

    Note:
        The docs directory is excluded because it often contains namespace-like
        structures that aren't actual Python packages.

    Example:
        >>> from pyrig.dev.utils.packages import get_namespace_packages
        >>> ns_pkgs = get_namespace_packages()
        >>> print(ns_pkgs)
        ['myproject.plugins', 'myproject.extensions']
    """
    logger.debug("Discovering namespace packages")
    packages = find_packages(depth=None)
    namespace_packages = find_packages(depth=None, include_namespace_packages=True)
    namespace_packages = [
        p for p in namespace_packages if not p.startswith(DOCS_DIR_NAME)
    ]
    # exclude all that are in .gitignore
    namespace_packages = [p for p in namespace_packages if not path_is_in_gitignore(p)]
    result = list(set(namespace_packages) - set(packages))
    logger.debug("Found %d namespace packages: %s", len(result), result)
    return result
