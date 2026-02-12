"""module."""

from pathlib import Path

from pyrig.rig.configs.issue_templates.config import ConfigConfigFile


class TestConfigConfigFile:
    """Test class."""

    def test_parent_path(self) -> None:
        """Test method."""
        result = ConfigConfigFile.parent_path()
        assert result == Path(".github/ISSUE_TEMPLATE")

    def test__configs(self) -> None:
        """Test method."""
        result = ConfigConfigFile._configs()  # noqa: SLF001
        assert isinstance(result, dict)

    def test_is_correct(self) -> None:
        """Test method."""
        assert ConfigConfigFile().is_correct()
