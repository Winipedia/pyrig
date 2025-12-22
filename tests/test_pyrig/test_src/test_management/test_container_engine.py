"""module."""

from pyrig.src.management.container_engine import ContainerEngine


class TestContainerEngine:
    """Test class."""

    def test_name(self) -> None:
        """Test method."""
        result = ContainerEngine.name()
        assert result == "podman"

    def test_get_build_args(self) -> None:
        """Test method."""
        result = ContainerEngine.get_build_args("-t", "myimage")
        assert result == ("podman", "build", "-t", "myimage")

    def test_get_save_args(self) -> None:
        """Test method."""
        result = ContainerEngine.get_save_args("-o", "image.tar")
        assert result == ("podman", "save", "-o", "image.tar")
