"""Helper functions for working with Python packages."""

from collections.abc import Iterable
from importlib import import_module
from pathlib import Path
from types import ModuleType

from setuptools import find_namespace_packages as _find_namespace_packages
from setuptools import find_packages as _find_packages

import pyrig
from pyrig.src.modules.package import DOCS_DIR_NAME
from pyrig.src.modules.path import ModulePath
from pyrig.src.testing.convention import TESTS_PACKAGE_NAME


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


def get_src_package() -> ModuleType:
    """Identify and return the main source package of the project.

    Discovers the main source package by finding all top-level packages
    and filtering out the test package. This is useful for automatically
    determining the package that contains the actual implementation code.

    Returns:
        The main source package as a module object

    Raises:
        ModuleNotFoundError: if the detection is not reliable

    """
    package_names = find_packages(depth=0, include_namespace_packages=False)
    package_paths = [ModulePath.pkg_name_to_relative_dir_path(p) for p in package_names]
    pkgs = [p for p in package_paths if p.name not in {TESTS_PACKAGE_NAME}]
    if len(pkgs) != 1:
        msg = "Could not reliably determine source package."
        raise ModuleNotFoundError(msg)
    pkg = pkgs[0]
    pkg_name = pkg.name

    return import_module(pkg_name)


def src_pkg_is_pyrig() -> bool:
    """Checks if the current project is pyrig itself.

    Returns:
        bool: True if pyrig is the current package and project, False otherwise
    """
    pkgs = find_packages(depth=0, include_namespace_packages=False)
    return pyrig.__name__ in pkgs


def get_namespace_packages() -> list[str]:
    """Get all namespace packages."""
    packages = find_packages(depth=None)
    namespace_packages = find_packages(depth=None, include_namespace_packages=True)
    namespace_packages = [
        p for p in namespace_packages if not p.startswith(DOCS_DIR_NAME)
    ]
    return list(set(namespace_packages) - set(packages))
