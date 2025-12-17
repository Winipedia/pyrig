"""Helper functions for working with Python packages."""

from collections.abc import Iterable
from importlib import import_module
from pathlib import Path
from types import ModuleType

from setuptools import find_namespace_packages as _find_namespace_packages
from setuptools import find_packages as _find_packages

from pyrig.src.modules.module import to_path
from pyrig.src.modules.package import DOCS_DIR_NAME
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
        StopIteration: If no source package can be found or
                       if only the test package exists

    """
    package_names = find_packages(depth=0, include_namespace_packages=False)
    package_paths = [to_path(p, is_package=True) for p in package_names]
    pkg = next(
        p for p in package_paths if p.name not in {TESTS_PACKAGE_NAME, DOCS_DIR_NAME}
    )
    pkg_name = pkg.name

    return import_module(pkg_name)
