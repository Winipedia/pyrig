"""Base exception for errors related to DependencySubclass in Pyrig."""

import pyrig
from pyrig.core.exceptions.base.dependency import DependencyError
from pyrig.core.string_ import snake_to_kebab_case
from pyrig.rig.cli.subcommands import subcls


class DependencySubclassError(DependencyError):
    """Raised when exceptions related to the DependencySubclass occur."""

    def command_recommendation(self) -> str:
        """Get a string recommending the proper command to generate subclasses."""
        return f"""Consider using the proper command to generate proper subclases:
        {snake_to_kebab_case(pyrig.__name__)} {snake_to_kebab_case(subcls.__name__)}"""
