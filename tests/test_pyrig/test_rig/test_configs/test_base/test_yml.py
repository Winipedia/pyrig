"""module."""

from pyrig.rig.configs.base.yml import YmlConfigFile
from pyrig.rig.configs.docs.docs_builder import DocsBuilderConfigFile


class TestYmlConfigFile:
    """Test class."""

    def test_extension(self) -> None:
        """Test method."""
        assert issubclass(DocsBuilderConfigFile, YmlConfigFile)
        extension = DocsBuilderConfigFile.I.extension()
        assert extension == "yml"


class TestDictYmlConfigFile:
    """Test class."""
