"""CLI command module for the ``pyrig init`` subcommand.

Provides the thin adapter function that the CLI invokes when a user runs
``pyrig init``. All orchestration logic lives in the tools layer.
"""

from pyrig.rig.tools.pyrigger import Pyrigger


def init_project() -> None:
    """Run the full pyrig project initialization sequence.

    This function is the CLI entry point for ``pyrig init``. It delegates
    entirely to ``Pyrigger.I.init_project``, which owns and executes all
    ordered setup steps.
    """
    Pyrigger.I.init_project()
