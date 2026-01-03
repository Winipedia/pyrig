"""module."""

from pathlib import Path

from pyrig.dev.configs.containers.container_file import ContainerfileConfigFile


class TestContainerfileConfigFile:
    """Test class."""

    def test_get_filename(self) -> None:
        """Test method."""
        assert ContainerfileConfigFile.get_filename() == "Containerfile"

    def test_get_parent_path(self) -> None:
        """Test method."""
        assert ContainerfileConfigFile.get_parent_path() == Path()

    def test_get_file_extension(self) -> None:
        """Test method."""
        assert ContainerfileConfigFile.get_file_extension() == ""

    def test_get_extension_sep(self) -> None:
        """Test method."""
        assert ContainerfileConfigFile.get_extension_sep() == ""

    def test_get_lines(self) -> None:
        """Test method."""
        layers = ContainerfileConfigFile.get_layers()
        lines = ContainerfileConfigFile.get_lines()
        content = "\n".join(lines)
        assert all(layer in content for layer in layers)

    def test_is_correct(self) -> None:
        """Test method."""
        assert ContainerfileConfigFile().is_correct()

    def test_get_layers(self) -> None:
        """Test method."""
        layers = ContainerfileConfigFile.get_layers()
        assert len(layers) > 0
