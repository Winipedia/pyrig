"""module."""

from pathlib import Path

from pyrig.rig.configs.markdown.contributing import ContributingConfigFile


class TestContributingConfigFile:
    """Test class."""

    def test_filename(self) -> None:
        """Test method."""
        result = ContributingConfigFile.filename()
        assert result == "CONTRIBUTING"

    def test_parent_path(self) -> None:
        """Test method."""
        result = ContributingConfigFile.parent_path()
        assert result == Path()

    def test_lines(self) -> None:
        """Test method."""
        result = ContributingConfigFile.lines()
        assert len(result) > 0

    def test_is_correct(self) -> None:
        """Test method."""
        result = ContributingConfigFile.is_correct()
        assert result
