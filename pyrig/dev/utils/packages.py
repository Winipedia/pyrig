"""Package discovery and source package identification utilities.

This module provides utilities for discovering Python packages in a project and
identifying the main source package. It wraps setuptools' package discovery
functions with additional filtering capabilities and integrates with pyrig's
conventions for test and documentation directories.

The module automatically excludes packages listed in .gitignore when discovering
packages, preventing discovery of packages in virtual environments, build
directories, and other ignored locations.

Functions:
    find_packages: Discover Python packages with depth and pattern filtering
    get_src_package: Identify and import the main source package of the project
    src_pkg_is_pyrig: Check if the current project is pyrig itself
    get_namespace_packages: Find all PEP 420 namespace packages in the project

Examples:
    Discover the main source package::

        >>> from pyrig.dev.utils.packages import get_src_package
        >>> src_pkg = get_src_package()
        >>> print(src_pkg.__name__)
        'myproject'
        >>> print(src_pkg.__file__)
        '/path/to/project/myproject/__init__.py'

    Find all packages with depth limit::

        >>> from pyrig.dev.utils.packages import find_packages
        >>> top_level = find_packages(depth=0)
        >>> print(top_level)
        ['myproject', 'tests']

    Check if running in pyrig development mode::

        >>> from pyrig.dev.utils.packages import src_pkg_is_pyrig
        >>> if src_pkg_is_pyrig():
        ...     print("Running in pyrig development mode")

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

    Wraps setuptools' package discovery functions with additional filtering
    capabilities. Automatically excludes packages listed in .gitignore to prevent
    discovering packages in virtual environments, build directories, and other
    ignored locations.

    Args:
        depth: Maximum depth of package nesting to include. For example:

            - depth=0: Only top-level packages (e.g., "myproject", "tests")
            - depth=1: Top-level and one level of subpackages (e.g., "myproject.utils")
            - None: Unlimited depth (all nested packages)

        include_namespace_packages: If True, includes PEP 420 namespace packages
            (packages without `__init__.py` files). If False, only includes regular
            packages with `__init__.py` files.
        where: Root directory to search for packages. Defaults to current directory
            ("."). Can be an absolute or relative path.
        exclude: Iterable of glob patterns for package names to exclude. If None,
            automatically reads .gitignore and converts directory patterns to package
            patterns (e.g., "build/" becomes "build"). Patterns support wildcards
            (e.g., "tests*" excludes "tests", "tests_integration", etc.).
        include: Iterable of glob patterns for package names to include. Defaults
            to all packages ("*"). Can be used to limit discovery to specific
            package prefixes.

    Returns:
        A list of discovered package names as dot-separated strings, sorted by
        setuptools' default ordering. For example: ["mypackage", "mypackage.core",
        "mypackage.utils"]. Returns an empty list if no packages are found.

    Examples:
        Find only top-level packages::

            >>> from pyrig.dev.utils.packages import find_packages
            >>> find_packages(depth=0)
            ['myproject', 'tests']

        Find all packages including namespace packages::

            >>> find_packages(include_namespace_packages=True)
            ['myproject', 'myproject.utils', 'myproject.core']

        Find packages excluding tests::

            >>> find_packages(exclude=['tests*'])
            ['myproject', 'myproject.utils']

        Find packages in a specific directory::

            >>> find_packages(where="src", depth=1)
            ['myproject', 'myproject.utils']

    Note:
        When exclude is None, the function reads .gitignore and converts directory
        patterns (ending with "/") to package patterns by replacing "/" with "."
        and removing the trailing dot. This ensures gitignored directories are
        automatically excluded from package discovery.
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
    filtering out the tests package. This is useful for automatically determining
    the package that contains the actual implementation code, as opposed to test
    code.

    The function assumes a standard Python project structure where there is exactly
    one top-level package that is not the tests package:

        project/
        ├── myproject/      # <- This is the source package (returned)
        │   ├── __init__.py
        │   ├── core.py
        │   └── utils/
        └── tests/          # <- Excluded from consideration
            ├── __init__.py
            └── test_core.py

    Returns:
        The main source package as an imported module object. This is the actual
        Python module, not just the package name string. You can access all module
        attributes like __name__, __file__, __version__, etc.

    Raises:
        ModuleNotFoundError: If the source package cannot be reliably determined.
            This occurs when:

            - There are zero non-test top-level packages
            - There are multiple non-test top-level packages
            - The identified package cannot be imported

    Examples:
        Get the source package and access its attributes::

            >>> from pyrig.dev.utils.packages import get_src_package
            >>> pkg = get_src_package()
            >>> print(pkg.__name__)
            'myproject'
            >>> print(pkg.__file__)
            '/path/to/project/myproject/__init__.py'

        Use the source package to access its contents::

            >>> pkg = get_src_package()
            >>> from importlib import import_module
            >>> core_module = import_module(f"{pkg.__name__}.core")

    Note:
        This function only considers regular packages (with __init__.py files),
        not namespace packages. It uses find_packages(depth=0) to discover only
        top-level packages.
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
    checking if "pyrig" is among the top-level packages. This is useful for
    conditional logic that should only execute when developing pyrig itself.

    Returns:
        True if the current project is pyrig (i.e., "pyrig" is a top-level package
        in the current directory), False otherwise.

    Examples:
        Conditional logic for pyrig development::

            >>> from pyrig.dev.utils.packages import src_pkg_is_pyrig
            >>> if src_pkg_is_pyrig():
            ...     print("Running in pyrig development mode")
            ...     # Update resource files, run pyrig-specific tests, etc.

        Skip certain operations when not in pyrig::

            >>> if not src_pkg_is_pyrig():
            ...     print("Running in a user project")
            ...     # Use pyrig as a library

    Note:
        This function checks for the presence of "pyrig" as a top-level package,
        not whether pyrig is installed. It's specifically for detecting when you're
        working within the pyrig repository itself, not when using pyrig as a
        dependency in another project.
    """
    pkgs = find_packages(depth=0, include_namespace_packages=False)
    return pyrig.__name__ in pkgs


def get_namespace_packages() -> list[str]:
    """Find all PEP 420 namespace packages in the project.

    Namespace packages (PEP 420) are packages without `__init__.py` files. This
    function discovers all namespace packages by comparing the results of
    find_namespace_packages (which includes both regular and namespace packages)
    with find_packages (which only includes regular packages).

    The function automatically excludes:

    - Packages in the docs directory (often contains non-package directory structures)
    - Packages matching .gitignore patterns (virtual environments, build dirs, etc.)

    Returns:
        A list of namespace package names as dot-separated strings. For example:
        ["myproject.plugins", "myproject.extensions"]. Returns an empty list if
        no namespace packages are found.

    Examples:
        Find all namespace packages::

            >>> from pyrig.dev.utils.packages import get_namespace_packages
            >>> ns_pkgs = get_namespace_packages()
            >>> print(ns_pkgs)
            ['myproject.plugins', 'myproject.extensions']

        Check if a project uses namespace packages::

            >>> ns_pkgs = get_namespace_packages()
            >>> if ns_pkgs:
            ...     print(f"Found {len(ns_pkgs)} namespace packages")
            ... else:
            ...     print("No namespace packages found")

    Note:
        The docs directory is excluded because it often contains directory
        structures that look like packages but aren't meant to be imported as
        Python modules (e.g., MkDocs documentation directories).

    See Also:
        PEP 420: Implicit Namespace Packages
        find_packages: For discovering regular packages only
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
