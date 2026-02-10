"""module."""

from pathlib import Path

from pyrig.rig.configs.markdown.contributing import ContributingConfigFile


class TestContributingConfigFile:
    """Test class."""

    def test_get_filename(self) -> None:
        """Test method."""
        result = ContributingConfigFile.get_filename()
        assert result == "CONTRIBUTING"

    def test_get_parent_path(self) -> None:
        """Test method."""
        result = ContributingConfigFile.get_parent_path()
        assert result == Path()

    def test_get_lines(self) -> None:
        """Test method."""
        result = ContributingConfigFile.get_lines()
        assert len(result) > 0

    def test_is_correct(self) -> None:
        """Test method."""
        result = ContributingConfigFile.is_correct()
        assert result
