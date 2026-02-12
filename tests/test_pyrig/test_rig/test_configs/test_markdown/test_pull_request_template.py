"""module."""

from pathlib import Path

from pyrig.rig.configs.markdown.pull_request_template import (
    PullRequestTemplateConfigFile,
)


class TestPullRequestTemplateConfigFile:
    """Test class."""

    def test_parent_path(self) -> None:
        """Test method."""
        result = PullRequestTemplateConfigFile.parent_path()
        assert result == Path(".github")

    def test_lines(self) -> None:
        """Test method."""
        result = PullRequestTemplateConfigFile.lines()
        assert len(result) > 0

    def test_is_correct(self) -> None:
        """Test method."""
        result = PullRequestTemplateConfigFile.is_correct()
        assert result
