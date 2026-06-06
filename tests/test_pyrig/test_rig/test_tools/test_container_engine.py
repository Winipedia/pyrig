"""module."""

from pathlib import Path

from pyrig.rig.tools import container_engine
from pyrig.rig.tools.container_engine import ContainerEngine


class TestContainerEngine:
    """Test class."""

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            ContainerEngine.I.image_url()
            == "https://img.shields.io/badge/Container-Podman-A23CD6?logo=podman&logoColor=grey&colorA=0D1F3F&colorB=A23CD6"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert ContainerEngine.I.link_url() == "https://podman.io"

    def test_group(self) -> None:
        """Test method."""
        result = ContainerEngine.I.group()
        assert isinstance(result, str)
        assert result == "tooling"

    def test_dev_dependencies(self) -> None:
        """Test method."""
        result = ContainerEngine.I.dev_dependencies()
        assert result == ()

    def test_name(self) -> None:
        """Test method."""
        result = ContainerEngine.I.name()
        assert result == "podman"

    def test_build_args(self) -> None:
        """Test method."""
        result = ContainerEngine.I.build_args(project_name="myimage")
        assert result == ("podman", "build", "-t", "myimage", ".")

    def test_save_args(self) -> None:
        """Test method."""
        image_file = Path("image.tar")
        image_path = Path("dist") / image_file
        result = ContainerEngine.I.save_args(
            image_path=image_path,
        )
        assert result == (
            "podman",
            "save",
            "-o",
            image_path.as_posix(),
            image_file.stem,
        )


def test_module_docstring() -> None:
    """Test module docstring."""
    assert (
        container_engine.__doc__
        == """Container engine wrapper.

Wraps container engine commands and information.
"""
    )
