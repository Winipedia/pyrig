"""Package discovery utilities for Python projects.

Extends setuptools' package discovery to locate packages across both
the source root and tests directory of a project.
"""

import logging
from collections.abc import Generator

from setuptools import find_namespace_packages as _find_namespace_packages
from setuptools import find_packages as _find_packages

from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.project_tester import ProjectTester

logger = logging.getLogger(__name__)


def find_namespace_packages() -> Generator[str, None, None]:
    """Yield packages that exist only as implicit namespace packages.

    Compares full namespace-package discovery (including directories without
    ``__init__.py``) against regular package discovery, then yields every name
    present in the namespace set but absent from the regular set.

    Implicit namespace packages are directories that Python treats as packages
    without requiring an ``__init__.py`` file.

    Returns:
        Generator of dot-separated package name strings for each discovered
        namespace-only package. Yields nothing if no namespace packages exist.
    """
    logger.debug("Discovering namespace packages")
    namespace_packages = find_packages(
        include_namespace_packages=True,
    )

    packages = set(find_packages())
    return (p for p in namespace_packages if p not in packages)


def find_packages(
    *,
    include_namespace_packages: bool = False,
) -> tuple[str, ...]:
    """Discover Python packages across the tests and source directories.

    Searches two locations: the project root (restricted to the tests package
    and its sub-packages) and the configured source root (e.g. ``src/``).
    Results from both locations are combined into a single tuple.

    Args:
        include_namespace_packages: When ``True``, also discovers implicit
            namespace packages (directories without ``__init__.py``).
            Defaults to ``False``.

    Returns:
        Tuple of dot-separated package name strings. Empty tuple if no
        packages are found.
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
