"""module."""

from pathlib import Path

from pyrig.rig.configs.containers.container_file import ContainerfileConfigFile


class TestContainerfileConfigFile:
    """Test class."""

    def test_filename(self) -> None:
        """Test method."""
        assert ContainerfileConfigFile.filename() == "Containerfile"

    def test_parent_path(self) -> None:
        """Test method."""
        assert ContainerfileConfigFile.parent_path() == Path()

    def test_extension(self) -> None:
        """Test method."""
        assert ContainerfileConfigFile.extension() == ""

    def test_extension_separator(self) -> None:
        """Test method."""
        assert ContainerfileConfigFile.extension_separator() == ""

    def test_lines(self) -> None:
        """Test method."""
        layers = ContainerfileConfigFile.layers()
        lines = ContainerfileConfigFile.lines()
        content = "\n".join(lines)
        assert all(layer in content for layer in layers)

    def test_is_correct(self) -> None:
        """Test method."""
        assert ContainerfileConfigFile.is_correct()

    def test_layers(self) -> None:
        """Test method."""
        layers = ContainerfileConfigFile.layers()
        assert len(layers) > 0
