"""module."""

from pyrig.rig.configs.base.yml import YmlConfigFile
from pyrig.rig.configs.docs.mkdocs import MkdocsConfigFile


class TestYmlConfigFile:
    """Test class."""

    def test_extension(self) -> None:
        """Test method."""
        assert issubclass(MkdocsConfigFile, YmlConfigFile)
        extension = MkdocsConfigFile.I.extension()
        assert extension == "yml"


class TestDictYmlConfigFile:
    """Test class."""
