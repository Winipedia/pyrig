"""module."""

from pathlib import Path

from pyrig.dev.management.container_engine import ContainerEngine


class TestContainerEngine:
    """Test class."""

    def test_name(self) -> None:
        """Test method."""
        result = ContainerEngine.name()
        assert result == "podman"

    def test_get_build_args(self) -> None:
        """Test method."""
        result = ContainerEngine.get_build_args(project_name="myimage")
        assert result == ("podman", "build", "-t", "myimage", ".")

    def test_get_save_args(self) -> None:
        """Test method."""
        image_file = Path("image.tar")
        image_path = Path("dist") / image_file
        result = ContainerEngine.get_save_args(
            image_file=image_file,
            image_path=image_path,
        )
        assert result == (
            "podman",
            "save",
            "-o",
            image_path.as_posix(),
            image_file.stem,
        )
