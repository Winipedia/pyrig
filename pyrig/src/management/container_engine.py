"""Container engine management utilities.

This module provides utilities for managing container engines,
specifically podman. It centralizes command construction for common
container management tasks.
"""

from pyrig.src.management.base.base import Args, Tool


class ContainerEngine(Tool):
    """Podman container engine tool.

    Provides methods for constructing podman command arguments for
    building and managing containers.
    """

    @classmethod
    def name(cls) -> str:
        """Get the tool name.

        Returns:
            str: The string 'podman'.
        """
        return "podman"

    @classmethod
    def get_build_args(cls, *args: str) -> Args:
        """Construct podman build command arguments.

        Args:
            *args: Additional arguments to append to the build command.

        Returns:
            Args: Command arguments for 'podman build'.
        """
        return cls.get_args("build", *args)

    @classmethod
    def get_save_args(cls, *args: str) -> Args:
        """Construct podman save command arguments.

        Args:
            *args: Additional arguments to append to the save command.

        Returns:
            Args: Command arguments for 'podman save'.
        """
        return cls.get_args("save", *args)
