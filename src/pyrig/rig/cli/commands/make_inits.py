"""`__init__.py` file creation for namespace packages.

Automatically creates `__init__.py` files for namespace packages (PEP 420
packages without `__init__.py`) to ensure proper importability.
"""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from pyrig.core.iterate import generator_has_items
from pyrig.core.modules.path import ModulePath, make_init_module
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.programming_language import ProgrammingLanguage
from pyrig.rig.tools.project_tester import ProjectTester
from pyrig.rig.utils.packages import find_namespace_packages


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
        ModulePath.package_name_to_relative_dir_path(
            package,
            root=ProjectTester.I.tests_source_root()
            if package.startswith(ProjectTester.I.tests_package_name())
            else PackageManager.I.source_root(),
        )
        for package in namespace_packages
    )

    def make_init_module_with_content(path: Path) -> None:
        """Make an __init__.py file with standard content."""
        make_init_module(
            path,
            content=ProgrammingLanguage.I.standard_init_content(),
        )

    with ThreadPoolExecutor() as executor:
        list(executor.map(make_init_module_with_content, package_paths))
