"""Podman container engine wrapper.

Provides type-safe wrapper for Podman commands (build, save).
Used for creating containerized builds, particularly PyInstaller executables.

Example:
    >>> from pyrig.dev.management.container_engine import ContainerEngine
    >>> build_args = ContainerEngine.L.get_build_args(project_name="myapp")
    >>> build_args.run()
"""

from pathlib import Path

from pyrig.dev.management.base.base import Tool
from pyrig.src.processes import Args


class ContainerEngine(Tool):
    """Podman container engine wrapper.

    Constructs podman command arguments for building and saving container images.

    Example:
        >>> from pathlib import Path
        >>> ContainerEngine.L.get_build_args(project_name="app:v1").run()
        >>> ContainerEngine.L.get_save_args(
        ...     image_file=Path("app.tar"), image_path=Path("./dist")
        ... ).run()
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
            *args: Additional build command arguments.
            project_name: Image tag for the build (e.g., "myapp" or "myapp:v1").

        Returns:
            Args for 'podman build'.
        """
        return cls.get_args("build", "-t", project_name, ".", *args)

    @classmethod
    def get_save_args(cls, *args: str, image_file: Path, image_path: Path) -> Args:
        """Construct podman save arguments.

        Args:
            *args: Additional save command arguments.
            image_file: Path representing the archive filename; `.stem` is used
                as the image name (e.g., Path("myapp.tar") yields image "myapp").
            image_path: Full output path for the saved archive (e.g., "dist/myapp.tar").

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
