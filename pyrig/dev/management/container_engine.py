"""Podman container engine wrapper.

Provides type-safe wrapper for Podman commands (build, save).
Used for creating containerized builds, particularly PyInstaller executables.

Example:
    >>> from pyrig.dev.management.container_engine import ContainerEngine
    >>> build_args = ContainerEngine.L.get_build_args("-t", "myapp:latest", ".")
    >>> build_args.run()
"""

from pathlib import Path

from pyrig.dev.management.base.base import Tool
from pyrig.src.processes import Args


class ContainerEngine(Tool):
    """Podman container engine wrapper.

    Constructs podman command arguments for building and saving container images.

    Example:
        >>> ContainerEngine.L.get_build_args("-t", "app:v1", ".").run()
        >>> ContainerEngine.L.get_save_args("-o", "app.tar", "app:v1").run()
    """

    @classmethod
    def name(cls) -> str:
        """Get tool name.

        Returns:
            'podman'
        """
        return "podman"

    @classmethod
    def get_build_args(cls, *args: str, project_name: str) -> Args:
        """Construct podman build arguments.

        Args:
            *args: Build command arguments.
            project_name: Name of the project to build.

        Returns:
            Args for 'podman build'.
        """
        return cls.get_args("build", "-t", project_name, ".", *args)

    @classmethod
    def get_save_args(cls, *args: str, image_file: Path, image_path: Path) -> Args:
        """Construct podman save arguments.

        Args:
            *args: Save command arguments.
            image_file: Name of the image file to save.
            image_path: Path to the image file to save.

        Returns:
            Args for 'podman save'.
        """
        return cls.get_args(
            "save",
            "-o",
            image_path.as_posix(),
            image_file.stem,
            *args,
        )
