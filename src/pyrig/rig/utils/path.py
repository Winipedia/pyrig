"""Handle Module names and paths conversions and related utilities."""

from pathlib import Path

from pyrig.core.modules.path import module_name_as_path, package_name_as_path
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.project_tester import ProjectTester


def module_name_as_root_path(module_name: str) -> Path:
    """Convert a dotted module name to a path relative to the appropriate root.

    The appropriate root is determined by checking
    if the module name starts with the tests package name.
    If so, the tests source root is used; otherwise, the source root is used.
    Root directories are determined by the ProjectTester and
    PackageManager respectively.

    Args:
        module_name: Dotted Python module name (e.g., "package.subpackage.module").

    Returns:
        Relative path to the module file (e.g., "src/package/subpackage/module.py"
        or "package/subpackage/module.py") depending on the roots
    """
    root = (
        ProjectTester.I.tests_source_root()
        if module_name.startswith(ProjectTester.I.tests_package_name())
        else PackageManager.I.source_root()
    )
    return root / module_name_as_path(module_name)


def package_name_as_root_path(package_name: str) -> Path:
    """Convert a dotted package name to a path relative to the appropriate root.

    The appropriate root is determined by checking
    if the package name starts with the tests package name.
    If so, the tests source root is used; otherwise, the source root is used.
    Root directories are determined by the ProjectTester and
    PackageManager respectively.

    Args:
        package_name: Dotted Python package name (e.g., "package.subpackage").

    Returns:
        Relative path to the package directory (e.g., "src/package/subpackage"
        or "package/subpackage") depending on the roots
    """
    root = (
        ProjectTester.I.tests_source_root()
        if package_name.startswith(ProjectTester.I.tests_package_name())
        else PackageManager.I.source_root()
    )
    return root / package_name_as_path(package_name)
