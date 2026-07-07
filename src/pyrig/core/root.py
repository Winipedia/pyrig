"""Project root related utilities."""

import logging
from collections.abc import Iterator
from itertools import chain
from pathlib import Path

from pyrig.core.introspection.packages import make_init_files
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.programming_language import ProgrammingLanguage
from pyrig.rig.tools.testers.project import ProjectTester

logger = logging.getLogger(__name__)


def make_all_init_files() -> tuple[Path, ...]:
    """Create all missing `__init__.py` files in the project.

    Returns:
        Directories where `__init__.py` files were created. Empty if all
        already existed.
    """
    return make_init_files(
        namespace_package_paths(),
        content=ProgrammingLanguage.I.standard_init_content(),
    )


def namespace_package_paths() -> Iterator[Path]:
    """Yield project directories that lack an `__init__.py` file.

    Searches the source package root and tests package root, including each
    root itself and all subdirectories at any depth, skipping `__pycache__`
    directories.

    Yields:
        Each directory under the source or tests package root that has no
        `__init__.py`.
    """
    logger.debug("Discovering namespace packages")

    package_root, tests_package_root = (
        PackageManager.I.package_root(),
        ProjectTester.I.package_root(),
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
