"""module."""

from pathlib import Path

from pyrig.rig.configs.markdown.contributing import ContributingConfigFile


class TestContributingConfigFile:
    """Test class."""

    def test_is_correct(self) -> None:
        """Test method."""
        assert ContributingConfigFile.I.is_correct()

    def test_stem(self) -> None:
        """Test method."""
        result = ContributingConfigFile.I.stem()
        assert result == "CONTRIBUTING"

    def test_parent_path(self) -> None:
        """Test method."""
        result = ContributingConfigFile.I.parent_path()
        assert result == Path()

    def test_lines(self) -> None:
        """Test method."""
        result = ContributingConfigFile.I.lines()
        assert len(result) > 0
