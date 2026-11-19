"""Cleanup command for removing compiled Python bytecode cache directories."""

from pyrig.rig.tools.programming_language import ProgrammingLanguage


def remove_pycache() -> None:
    """Remove project-root and source/test-tree `__pycache__` directories."""
    ProgrammingLanguage.I.remove_pycache()
