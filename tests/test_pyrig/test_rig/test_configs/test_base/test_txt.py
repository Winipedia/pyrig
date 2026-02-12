"""module."""

from pyrig.rig.configs.base.txt import TxtConfigFile


class TestTxtConfigFile:
    """Test class."""

    def test_extension(self) -> None:
        """Test method."""
        extension = TxtConfigFile.extension()
        assert extension == "txt"
