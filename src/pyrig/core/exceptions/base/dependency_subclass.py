"""Base exception for errors related to DependencySubclass in Pyrig."""

from pyrig.core.exceptions.base.dependency import DependencyError
from pyrig.rig.cli.subcommands import subcls
from pyrig.rig.tools.pyrigger import Pyrigger


class DependencySubclassError(DependencyError):
    """Raised when exceptions related to the DependencySubclass occur."""

    def command_recommendation(self) -> str:
        """Get a string recommending the proper command to generate subclasses."""
        return f"""Consider using the proper command to generate proper subclases:
        '{Pyrigger.I.cmd_args(cmd=subcls)}'"""
