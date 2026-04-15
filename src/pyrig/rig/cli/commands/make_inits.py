"""`__init__.py` file creation for namespace packages.

Automatically creates `__init__.py` files for namespace packages (PEP 420
packages without `__init__.py`) to ensure proper importability.
"""

from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from pyrig.core.introspection.packages import make_init_file
from pyrig.core.iterate import generator_has_items
from pyrig.rig.tools.programming_language import ProgrammingLanguage
from pyrig.rig.utils.packages import find_namespace_packages
from pyrig.rig.utils.path import package_name_as_root_path


def make_init_files() -> None:
    """Create `__init__.py` files for all namespace packages.

    Scans the project for namespace packages (directories with Python files
    but no `__init__.py`) and creates minimal `__init__.py` files for them.

    Idempotent. Uses parallel execution for performance.

    Note:
        Created `__init__.py` files contain a minimal docstring. The docs
        directory is excluded from scanning.
    """
    namespace_packages = find_namespace_packages()
    has_namespace_packages, namespace_packages = generator_has_items(namespace_packages)
    if not has_namespace_packages:
        return

    # make init files for all namespace packages
    package_paths = (
        package_name_as_root_path(package) for package in namespace_packages
    )

    def make_init_file_with_content(path: Path) -> None:
        """Make an __init__.py file with standard content."""
        make_init_file(
            path,
            content=ProgrammingLanguage.I.standard_init_content(),
        )

    with ThreadPoolExecutor() as executor:
        list(executor.map(make_init_file_with_content, package_paths))


def make_init_files_for_namespace_packages(namespace_packages: Iterable[str]) -> None:
    """Create `__init__.py` files for the given namespace packages.

    Args:
        namespace_packages: An iterable of namespace package names.
            These are the dotted package names (e.g. `myproject.mypackage`).
    """
    package_paths = (
        package_name_as_root_path(package) for package in namespace_packages
    )

    with ThreadPoolExecutor() as executor:
        list(executor.map(make_init_file_with_standard_content, package_paths))


def make_init_file_with_standard_content(path: Path) -> None:
    """Make an __init__.py file with standard content."""
    make_init_file(
        path,
        content=ProgrammingLanguage.I.standard_init_content(),
    )
