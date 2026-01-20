"""module."""

from pathlib import Path

from pyrig.dev.configs.markdown.pull_request_template import (
    PullRequestTemplateConfigFile,
)


class TestPullRequestTemplateConfigFile:
    """Test class."""

    def test_get_parent_path(self) -> None:
        """Test method."""
        result = PullRequestTemplateConfigFile.get_parent_path()
        assert result == Path(".github")

    def test_get_lines(self) -> None:
        """Test method."""
        result = PullRequestTemplateConfigFile.get_lines()
        assert len(result) > 0

    def test_is_correct(self) -> None:
        """Test method."""
        result = PullRequestTemplateConfigFile.is_correct()
        assert result
