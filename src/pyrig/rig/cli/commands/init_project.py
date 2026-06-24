"""Entry point for the `pyrig init` command."""

from pyrig.rig.tools.pyrigger import Pyrigger


def init_project() -> None:
    """Run the full pyrig project initialization sequence."""
    Pyrigger.I.init_project()
