"""Package discovery and ``__init__.py`` management utilities.

Extends setuptools' package discovery to locate packages across both the
source root and tests directory of a project, and creates missing
``__init__.py`` files for any implicit namespace packages that are found.
"""

import logging
from collections.abc import Iterable, Iterator

from setuptools import find_namespace_packages as _find_namespace_packages
from setuptools import find_packages as _find_packages

from pyrig.core.introspection.packages import make_init_file
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.programming_language import ProgrammingLanguage
from pyrig.rig.tools.project_tester import ProjectTester
from pyrig.rig.utils.paths import package_name_as_root_path

logger = logging.getLogger(__name__)


def make_init_files() -> None:
    """Create `__init__.py` files for all namespace packages in the project.

    Discovers namespace packages by scanning the tests and source directories
    and creates a minimal `__init__.py` in each. Idempotent: packages that
    already have an `__init__.py` are skipped.
    """
    make_init_files_for_namespace_packages(find_namespace_packages())


def make_init_files_for_namespace_packages(namespace_packages: Iterable[str]) -> None:
    """Create `__init__.py` files for the given namespace packages.

    Resolves each dotted package name to its filesystem path and writes a
    minimal `__init__.py` containing a standard package initialization
    docstring. Skips any package that already has an `__init__.py`.

    Args:
        namespace_packages: Dotted package names of namespace packages to
            initialize (e.g. ``"myproject.subpackage"``).
    """
    package_paths = (
        package_name_as_root_path(package) for package in namespace_packages
    )

    content = ProgrammingLanguage.I.standard_init_content()
    for package_path in package_paths:
        make_init_file(package_path, content)


def find_namespace_packages() -> Iterator[str]:
    """Yield packages that exist only as implicit namespace packages.

    Compares full namespace-package discovery (including directories without
    ``__init__.py``) against regular package discovery, then yields every name
    present in the namespace set but absent from the regular set.

    Implicit namespace packages are directories that Python treats as packages
    without requiring an ``__init__.py`` file.

    Returns:
        Iterator of dot-separated package name strings for each discovered
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
