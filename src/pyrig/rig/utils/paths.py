"""Utilities for resolving dotted Python names to project-rooted filesystem paths."""

from pathlib import Path

from pyrig.core.introspection.paths import module_name_as_path, package_name_as_path
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.project_tester import ProjectTester


def module_name_as_root_path(module_name: str) -> Path:
    """Resolve a dotted module name to its filesystem path relative to the project root.

    Selects the appropriate root directory based on the module's package:

    - Modules starting with the tests package name (e.g., ``"tests"``) are rooted
      at the tests source root, which is an empty path (the project root itself).
    - All other modules are rooted at the source root (e.g., ``src/``).

    Args:
        module_name: Dotted Python module name
            (e.g., ``"mypackage.sub.module"`` or ``"tests.test_sub.test_module"``).

    Returns:
        Path to the module's ``.py`` file relative to the project root
        (e.g., ``Path("src/mypackage/sub/module.py")`` for a source module, or
        ``Path("tests/test_sub/test_module.py")`` for a test module).
    """
    root = (
        ProjectTester.I.tests_source_root()
        if module_name.startswith(ProjectTester.I.tests_package_name())
        else PackageManager.I.source_root()
    )
    return root / module_name_as_path(module_name)


def package_name_as_root_path(package_name: str) -> Path:
    """Resolve a package name to its filesystem path relative to the project root.

    Selects the appropriate root directory based on the package:

    - Packages starting with the tests package name (e.g., ``"tests"``) are rooted
      at the tests source root, which is an empty path (the project root itself).
    - All other packages are rooted at the source root (e.g., ``src/``).

    Args:
        package_name: Dotted Python package name
            (e.g., ``"mypackage.sub"`` or ``"tests.test_sub"``).

    Returns:
        Path to the package directory relative to the project root
        (e.g., ``Path("src/mypackage/sub")`` for a source package, or
        ``Path("tests/test_sub")`` for a test package).
    """
    root = (
        ProjectTester.I.tests_source_root()
        if package_name.startswith(ProjectTester.I.tests_package_name())
        else PackageManager.I.source_root()
    )
    return root / package_name_as_path(package_name)
