"""Cleanup command for removing compiled Python bytecode cache directories."""

import shutil

import typer

from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.project_tester import ProjectTester


def remove_pycache() -> None:
    """Remove all __pycache__ directories in the project.

    Recursively scans the src and tests roots and deletes every __pycache__
    directory found, printing each path to standard output before removal.
    """
    roots = (ProjectTester.I.tests_package_root(), PackageManager.I.package_root())
    for root in roots:
        for pycache in root.rglob("__pycache__"):
            if pycache.is_dir():
                typer.echo(f"Removing {pycache}")
                shutil.rmtree(pycache)
