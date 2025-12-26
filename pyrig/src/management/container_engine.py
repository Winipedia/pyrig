"""Podman container engine wrapper for building and managing containers.

This module provides a type-safe wrapper for Podman container engine commands.
The `ContainerEngine` class constructs podman command arguments for building
container images and saving them to archives.

Podman is used in pyrig for creating containerized builds of applications,
particularly for PyInstaller-based executables that need to be built in
isolated environments.

Example:
    >>> from pyrig.src.management.container_engine import ContainerEngine
    >>> build_args = ContainerEngine.get_build_args("-t", "myapp:latest", ".")
    >>> print(build_args)
    podman build -t myapp:latest .
    >>> build_args.run()

See Also:
    pyrig.src.management.base.base.Tool: Base class for tool wrappers
    pyrig.dev.builders: Uses ContainerEngine for containerized builds
"""

from pyrig.src.management.base.base import Args, Tool


class ContainerEngine(Tool):
    """Podman container engine tool wrapper.

    Provides methods for constructing podman command arguments for building
    container images and saving them to archives. This is used primarily for
    creating isolated build environments for PyInstaller executables.

    All methods return `Args` objects that can be executed via `.run()` or
    converted to strings for display.

    Example:
        >>> build_args = ContainerEngine.get_build_args("-t", "app:v1", ".")
        >>> save_args = ContainerEngine.get_save_args("-o", "app.tar", "app:v1")
        >>> build_args.run()
        >>> save_args.run()

    See Also:
        pyrig.src.management.base.base.Tool: Base class
        pyrig.dev.builders.pyinstaller.PyInstallerBuilder: Uses this for builds
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
