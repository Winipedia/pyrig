"""Utilities for resolving dotted Python names to project-rooted filesystem paths."""

import logging
from collections.abc import Iterator
from itertools import chain
from pathlib import Path

from pyrig.core.introspection.packages import make_init_files
from pyrig.core.introspection.paths import (
    module_name_as_path,
    path_as_module_name,
)
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.programming_language import ProgrammingLanguage
from pyrig.rig.tools.testers.project import ProjectTester

logger = logging.getLogger(__name__)


def make_all_init_files() -> tuple[Path, ...]:
    """Create all missing __init__.py files in the project.

    Returns:
        Tuple of paths where ``__init__.py`` files were created.
        Empty if all already existed.
    """
    return make_init_files(
        namespace_package_paths(),
        content=ProgrammingLanguage.I.standard_init_content(),
    )


def namespace_package_paths() -> Iterator[Path]:
    """Yield packages that exist only as implicit namespace packages.

    Walks the source and tests package roots recursively, yielding every
    directory that lacks an ``__init__.py`` file. Directories named
    ``__pycache__`` are skipped.

    Implicit namespace packages are directories that Python treats as packages
    without requiring an ``__init__.py`` file.

    Returns:
        Iterator of ``Path`` objects for each directory that has no
        ``__init__.py``. Yields nothing if no namespace packages exist.
    """
    logger.debug("Discovering namespace packages")

    package_root, tests_package_root = (
        PackageManager.I.package_root(),
        ProjectTester.I.tests_package_root(),
    )
    for p in chain(
        (package_root, tests_package_root),
        package_root.rglob("*"),
        tests_package_root.rglob("*"),
    ):
        if not p.is_dir():
            continue
        if p.name == "__pycache__":
            continue
        init = p / "__init__.py"
        if init.exists():
            continue
        yield p


def root_path_as_module_name(path: Path) -> str:
    """Convert a filesystem path relative to the project root to a dotted module name.

    Selects the appropriate root directory based on the path.
    Paths starting with any source roots (e.g., ``src/``) are stripped
    from their root before constructing the resulting module name.

    Args:
        path: Filesystem path relative to the project root.

    Returns:
        Dotted Python module name (
            e.g., ``"mypackage.sub.module"`` or ``"tests.test_sub.test_module"``
        ).
    """
    if path.is_relative_to(PackageManager.I.source_root()):
        root = PackageManager.I.source_root()
    elif path.is_relative_to(ProjectTester.I.tests_source_root()):
        root = ProjectTester.I.tests_source_root()
    else:
        root = Path()
    relative_path = path.relative_to(root)
    return path_as_module_name(relative_path)


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
    return determine_root(module_name) / module_name_as_path(module_name)


def determine_root(module_name: str) -> Path:
    """Determines the root path of the given name."""
    return (
        ProjectTester.I.tests_source_root()
        if module_name.startswith(ProjectTester.I.tests_package_name())
        else PackageManager.I.source_root()
    )
