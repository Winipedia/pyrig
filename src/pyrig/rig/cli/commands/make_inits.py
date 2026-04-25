"""`__init__.py` file creation for namespace packages."""

from collections.abc import Iterable

from pyrig.core.introspection.packages import make_init_file
from pyrig.rig.tools.programming_language import ProgrammingLanguage
from pyrig.rig.utils.packages import find_namespace_packages
from pyrig.rig.utils.paths import package_name_as_root_path


def make_init_files() -> None:
    """Create `__init__.py` files for all namespace packages in the project.

    Discovers namespace packages by scanning the project (excluding the docs
    directory) and creates a minimal `__init__.py` in each. Idempotent:
    packages that already have an `__init__.py` are skipped.
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
