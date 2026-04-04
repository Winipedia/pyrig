"""Command to remove __pycache__ directories from tests and package.

This command recursively deletes all __pycache__ directories from the tests
package and the main package, cleaning up compiled Python files.
"""

import shutil

import typer

from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.project_tester import ProjectTester


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
    roots = (ProjectTester.I.tests_package_root(), PackageManager.I.package_root())
    for root in roots:
        for pycache in root.rglob("__pycache__"):
            if pycache.is_dir():
                typer.echo(f"Removing {pycache}")
                shutil.rmtree(pycache)
