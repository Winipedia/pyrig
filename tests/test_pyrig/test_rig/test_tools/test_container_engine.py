"""module."""

from pathlib import Path

from pyrig.rig.tools.container_engine import ContainerEngine


class TestContainerEngine:
    """Test class."""

    def test_get_group(self) -> None:
        """Test method."""
        result = ContainerEngine.L.get_group()
        assert isinstance(result, str)
        assert result == "tooling"

    def test_get_badge_urls(self) -> None:
        """Test method."""
        result = ContainerEngine.L.get_badge_urls()
        assert isinstance(result, tuple)
        assert all(isinstance(url, str) for url in result)

    def test_get_dev_dependencies(self) -> None:
        """Test method."""
        result = ContainerEngine.L.get_dev_dependencies()
        assert result == []

    def test_get_name(self) -> None:
        """Test method."""
        result = ContainerEngine.L.get_name()
        assert result == "podman"

    def test_get_build_args(self) -> None:
        """Test method."""
        result = ContainerEngine.L.get_build_args(project_name="myimage")
        assert result == ("podman", "build", "-t", "myimage", ".")

    def test_get_save_args(self) -> None:
        """Test method."""
        image_file = Path("image.tar")
        image_path = Path("dist") / image_file
        result = ContainerEngine.L.get_save_args(
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
