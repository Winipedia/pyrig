"""`__init__.py` file creation for namespace packages.

Automatically creates `__init__.py` files for namespace packages (PEP 420
packages without `__init__.py`) to ensure proper importability.
"""

from collections.abc import Iterable

from pyrig.core.introspection.packages import make_init_file
from pyrig.rig.tools.programming_language import ProgrammingLanguage
from pyrig.rig.utils.packages import find_namespace_packages
from pyrig.rig.utils.paths import package_name_as_root_path


def make_init_files() -> None:
    """Create `__init__.py` files for all namespace packages.

    Scans the project for namespace packages (directories with Python files
    but no `__init__.py`) and creates minimal `__init__.py` files for them.

    Idempotent. Uses parallel execution for performance.

    Note:
        Created `__init__.py` files contain a minimal docstring. The docs
        directory is excluded from scanning.
    """
    make_init_files_for_namespace_packages(find_namespace_packages())


def make_init_files_for_namespace_packages(namespace_packages: Iterable[str]) -> None:
    """Create `__init__.py` files for the given namespace packages.

    Args:
        namespace_packages: An iterable of namespace package names.
            These are the dotted package names (e.g. `myproject.mypackage`).
    """
    package_paths = (
        package_name_as_root_path(package) for package in namespace_packages
    )

    content = ProgrammingLanguage.I.standard_init_content()
    tuple(make_init_file(path=path, content=content) for path in package_paths)
