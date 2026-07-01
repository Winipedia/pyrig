"""Backend for the `init` CLI command that bootstraps a new pyrig project."""

from pyrig.rig.tools.pyrigger import Pyrigger


def init_project() -> None:
    """Run the full project initialization sequence."""
    Pyrigger.I.init_project()
