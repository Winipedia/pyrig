"""CLI command module for the `pyrig init` subcommand.

Provides the thin adapter function that the CLI invokes when a user runs
`pyrig init`. All orchestration logic lives in the tools layer.
"""

from pyrig.rig.tools.pyrigger import Pyrigger


def init_project() -> None:
    """Run the full pyrig project initialization sequence.

    Delegates to [Pyrigger][pyrig.rig.tools.pyrigger.Pyrigger], which owns
    and executes all ordered setup steps.
    """
    Pyrigger.I.init_project()
