"""module."""

from pathlib import Path

from pyrig.rig.configs.docs.mkdocs import MkdocsConfigFile


class TestMkdocsConfigFile:
    """Test class."""

    def test_get_parent_path(self) -> None:
        """Test method."""
        parent_path = MkdocsConfigFile.get_parent_path()
        assert parent_path == Path()

    def test__get_configs(self) -> None:
        """Test method."""
        configs = MkdocsConfigFile.get_configs()
        assert isinstance(configs, dict)
        assert "site_name" in configs
        assert "nav" in configs
        assert "plugins" in configs
        assert "theme" in configs
        assert isinstance(configs["theme"], dict)
        assert configs["theme"]["name"] == "material"
