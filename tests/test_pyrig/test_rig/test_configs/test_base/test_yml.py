"""module."""

from pyrig.rig.configs.base.yml import YMLConfigFile
from pyrig.rig.configs.docs.docs_builder import DocsBuilderConfigFile


class TestYMLConfigFile:
    """Test class."""

    def test_extension(self) -> None:
        """Test method."""
        assert issubclass(DocsBuilderConfigFile, YMLConfigFile)
        extension = DocsBuilderConfigFile.I.extension()
        assert extension == "yml"


class TestYMLDictConfigFile:
    """Test class."""
