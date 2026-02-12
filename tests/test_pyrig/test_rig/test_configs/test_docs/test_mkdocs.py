"""module."""

from pathlib import Path

from pyrig.rig.configs.docs.mkdocs import MkdocsConfigFile


class TestMkdocsConfigFile:
    """Test class."""

    def test_parent_path(self) -> None:
        """Test method."""
        parent_path = MkdocsConfigFile.parent_path()
        assert parent_path == Path()

    def test__configs(self) -> None:
        """Test method."""
        configs = MkdocsConfigFile.configs()
        assert isinstance(configs, dict)
        assert "site_name" in configs
        assert "nav" in configs
        assert "plugins" in configs
        assert "theme" in configs
        assert isinstance(configs["theme"], dict)
        assert configs["theme"]["name"] == "material"
