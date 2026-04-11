"""module."""

from pathlib import Path

from pyrig.rig.configs.docs.docs_builder import DocsBuilderConfigFile


class TestDocsBuilderConfigFile:
    """Test class."""

    def test_stem(self) -> None:
        """Test method."""
        assert DocsBuilderConfigFile.I.stem() == "mkdocs"

    def test_parent_path(self) -> None:
        """Test method."""
        parent_path = DocsBuilderConfigFile.I.parent_path()
        assert parent_path == Path()

    def test__configs(self) -> None:
        """Test method."""
        configs = DocsBuilderConfigFile.I.configs()
        assert isinstance(configs, dict)
        assert "site_name" in configs
        assert "nav" in configs
        assert "plugins" in configs
        assert "theme" in configs
        assert isinstance(configs["theme"], dict)
        assert configs["theme"]["name"] == "material"
