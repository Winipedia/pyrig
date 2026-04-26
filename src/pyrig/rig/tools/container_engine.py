"""Container engine wrapper.

Wraps container engine commands and information.
"""

from pathlib import Path

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Tool, ToolGroup


class ContainerEngine(Tool):
    """Container engine wrapper.

    Constructs podman command arguments for building and saving container images.
    Typical usage: call ``build_args`` to build the image, then ``save_args``
    to export it as a tar archive.

    Example:
        >>> from pathlib import Path
        >>> ContainerEngine.I.build_args(project_name="app:v1").run()
        >>> ContainerEngine.I.save_args(image_path=Path("dist/app.tar")).run()
    """

    def name(self) -> str:
        """Get tool name.

        Returns:
            'podman'
        """
        return "podman"

    def group(self) -> str:
        """Returns the group the tool belongs to.

        Returns:
            ``"tooling"``
        """
        return ToolGroup.TOOLING

    def badge_urls(self) -> tuple[str, str]:
        """Return the badge image URL and the project link URL.

        Returns:
            A two-element tuple where the first element is the shield badge
            image URL and the second is the URL that the badge links to.
        """
        return (
            "https://img.shields.io/badge/Container-Podman-A23CD6?logo=podman&logoColor=grey&colorA=0D1F3F&colorB=A23CD6",
            "https://podman.io",
        )

    def dev_dependencies(self) -> tuple[str, ...]:
        """Get tool dependencies.

        Podman is a system package (not a Python dependency), so this
        returns an empty list.

        Returns:
            Empty list — podman must be installed at the OS level.
        """
        return ()

    def build_args(self, *args: str, project_name: str) -> Args:
        """Construct podman build arguments.

        Args:
            *args: Additional build command arguments.
            project_name: Image tag for the build (e.g., "myapp" or "myapp:v1").

        Returns:
            Args for 'podman build'.
        """
        return self.args("build", "-t", project_name, ".", *args)

    def save_args(self, *args: str, image_path: Path) -> Args:
        """Construct podman save arguments.

        The image name passed to podman is derived from ``image_path.stem``
        (e.g., ``Path("dist/myapp.tar")`` yields image name ``"myapp"``), so
        the path stem must match the tag used when building the image.

        Args:
            *args: Additional save command arguments.
            image_path: Full output path for the saved tar archive
                (e.g., ``Path("dist/myapp.tar")``). The stem is used as the
                image name to export.

        Returns:
            Args for 'podman save'.
        """
        return self.args(
            "save",
            "-o",
            image_path.as_posix(),
            image_path.stem,
            *args,
        )
