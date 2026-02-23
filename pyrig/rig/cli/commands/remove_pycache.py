"""Command to remove __pycache__ directories from tests and package.

This command recursively deletes all __pycache__ directories from the tests
package and the main package, cleaning up compiled Python files.
"""

import logging
import shutil
from pathlib import Path

from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.project_tester import ProjectTester

logger = logging.getLogger(__name__)


def remove_pycache() -> None:
    """Remove all __pycache__ directories from tests and package.

    This function searches for __pycache__ directories within the tests package
    and the main package defined in pyproject.toml, and removes them along with
    their contents.

    Note:
        Use with caution, as this will permanently delete all __pycache__
        directories and their contents. Safe to run multiple times, as it only
        targets existing __pycache__ directories.
    """
    roots = (ProjectTester.I.tests_package_name(), PackageManager.I.package_name())
    for r in roots:
        root = Path(r)
        for pycache in root.rglob("__pycache__"):
            if pycache.is_dir():
                logger.info("Removing %s", pycache)
                shutil.rmtree(pycache)
