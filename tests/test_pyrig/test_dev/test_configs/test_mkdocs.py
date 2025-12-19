"""module."""

from pathlib import Path

from pyrig.dev.configs.mkdocs import MkdocsConfigFile


class TestMkdocsConfigFile:
    """Test class."""

    def test_get_parent_path(self) -> None:
        """Test method."""
        parent_path = MkdocsConfigFile.get_parent_path()
        assert parent_path == Path()

    def test_get_configs(self) -> None:
        """Test method."""
        configs = MkdocsConfigFile.get_configs()
        assert "site_name" in configs
        assert "nav" in configs
        assert "plugins" in configs
