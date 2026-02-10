"""module."""

from pyrig.rig.configs.base.yml import YmlConfigFile


class TestYmlConfigFile:
    """Test class."""

    def test_get_file_extension(self) -> None:
        """Test method."""
        extension = YmlConfigFile.get_file_extension()
        assert extension == "yml"
