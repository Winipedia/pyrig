"""Podman container engine wrapper.

Provides type-safe wrapper for Podman commands (build, save).
Used for creating containerized builds, particularly PyInstaller executables.

Example:
    >>> from pyrig.rig.tools.container_engine import ContainerEngine
    >>> args = ContainerEngine.I.build_args(project_name="myapp")
    >>> args.run()
"""

from pathlib import Path

from pyrig.rig.tools.base.base import Tool, ToolGroup
from pyrig.src.processes import Args


class ContainerEngine(Tool):
    """Podman container engine wrapper.

    Constructs podman command arguments for building and saving container images.

    Example:
        >>> from pathlib import Path
        >>> ContainerEngine.I.build_args(project_name="app:v1").run()
        >>> ContainerEngine.I.save_args(
        ...     image_file=Path("app.tar"), image_path=Path("dist/app.tar")
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
    def group(cls) -> str:
        """Return the badge group for this tool."""
        return ToolGroup.TOOLING

    @classmethod
    def badge_urls(cls) -> tuple[str, str]:
        """Return the badge and link URLs."""
        return (
            "https://img.shields.io/badge/Container-Podman-A23CD6?logo=podman&logoColor=grey&colorA=0D1F3F&colorB=A23CD6",
            "https://podman.io",
        )

    @classmethod
    def dev_dependencies(cls) -> list[str]:
        """Get tool dependencies.

        Podman is a system package (not a Python dependency), so this
        returns an empty list.

        Returns:
            Empty list — podman must be installed at the OS level.
        """
        return []

    @classmethod
    def build_args(cls, *args: str, project_name: str) -> Args:
        """Construct podman build arguments.

        Args:
            *args: Additional build command arguments.
            project_name: Image tag for the build (e.g., "myapp" or "myapp:v1").

        Returns:
            Args for 'podman build'.
        """
        return cls.args("build", "-t", project_name, ".", *args)

    @classmethod
    def save_args(cls, *args: str, image_file: Path, image_path: Path) -> Args:
        """Construct podman save arguments.

        Args:
            *args: Additional save command arguments.
            image_file: Path representing the archive filename; `.stem` is used
                as the image name (e.g., Path("myapp.tar") yields image "myapp").
            image_path: Full output path for the saved archive (e.g., "dist/myapp.tar").

        Returns:
            Args for 'podman save'.
        """
        return cls.args(
            "save",
            "-o",
            image_path.as_posix(),
            image_file.stem,
            *args,
        )
