"""Podman container engine wrapper.

Provides type-safe wrapper for Podman commands (build, save).
Used for creating containerized builds, particularly PyInstaller executables.

Example:
    >>> from pyrig.src.management.container_engine import ContainerEngine
    >>> build_args = ContainerEngine.get_build_args("-t", "myapp:latest", ".")
    >>> build_args.run()
"""

from pyrig.src.management.base.base import Tool
from pyrig.src.processes import Args


class ContainerEngine(Tool):
    """Podman container engine wrapper.

    Constructs podman command arguments for building and saving container images.

    Example:
        >>> ContainerEngine.get_build_args("-t", "app:v1", ".").run()
        >>> ContainerEngine.get_save_args("-o", "app.tar", "app:v1").run()
    """

    @classmethod
    def name(cls) -> str:
        """Get tool name.

        Returns:
            'podman'
        """
        return "podman"

    @classmethod
    def get_build_args(cls, *args: str) -> Args:
        """Construct podman build arguments.

        Args:
            *args: Build command arguments.

        Returns:
            Args for 'podman build'.
        """
        return cls.get_args("build", *args)

    @classmethod
    def get_save_args(cls, *args: str) -> Args:
        """Construct podman save arguments.

        Args:
            *args: Save command arguments.

        Returns:
            Args for 'podman save'.
        """
        return cls.get_args("save", *args)
