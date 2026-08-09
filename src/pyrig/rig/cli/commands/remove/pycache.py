"""Cleanup command for removing compiled Python bytecode cache directories."""

from pyrig.rig.tools.programming_language import ProgrammingLanguage


def remove_pycache() -> None:
    """Remove all `__pycache__` directories from the project's source and test trees."""
    ProgrammingLanguage.I.remove_pycache()
