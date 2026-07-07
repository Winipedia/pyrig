"""Cleanup command for removing compiled Python bytecode cache directories."""

import shutil

import typer

from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.testers.project import ProjectTester


def remove_pycache() -> None:
    """Remove all `__pycache__` directories in the project.

    Covers the package root and tests package root at all depths, echoing
    each removed path to standard output.
    """
    roots = (ProjectTester.I.package_root(), PackageManager.I.package_root())
    for root in roots:
        for pycache in root.rglob("__pycache__"):
            if pycache.is_dir():
                shutil.rmtree(pycache)
                typer.echo(f"Removed {pycache}")
