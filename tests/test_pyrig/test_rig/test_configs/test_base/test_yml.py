"""module."""

from pyrig.rig.configs.base.yml import YmlConfigFile


class TestYmlConfigFile:
    """Test class."""

    def test_extension(self) -> None:
        """Test method."""
        extension = YmlConfigFile.extension()
        assert extension == "yml"
