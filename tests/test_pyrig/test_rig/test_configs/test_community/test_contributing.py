"""module."""

from pathlib import Path

from pyrig.rig.configs.community.contributing import ContributingConfigFile


class TestContributingConfigFile:
    """Test class."""

    def test_stem(self) -> None:
        """Test method."""
        result = ContributingConfigFile.I.stem()
        assert result == "CONTRIBUTING"

    def test_parent_path(self) -> None:
        """Test method."""
        result = ContributingConfigFile.I.parent_path()
        assert result == Path()

    def test_content(self) -> None:
        """Test method."""
        result = ContributingConfigFile.I.content()
        assert len(result) > 0
