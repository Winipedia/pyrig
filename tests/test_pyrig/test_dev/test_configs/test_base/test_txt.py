"""module."""

from pyrig.dev.configs.base.txt import TxtConfigFile


class TestTxtConfigFile:
    """Test class."""

    def test_get_file_extension(self) -> None:
        """Test method."""
        extension = TxtConfigFile.get_file_extension()
        assert extension == "txt"
