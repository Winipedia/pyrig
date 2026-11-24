"""module."""

from pathlib import Path

from pyrig.rig.configs.version_control.remote.issue_templates.config import (
    IssueTemplateConfigFile,
)


class TestIssueTemplateConfigFile:
    """Test class."""

    def test__configs(self) -> None:
        """Test method."""
        result = IssueTemplateConfigFile.I._configs()  # noqa: SLF001
        assert isinstance(result, dict)

    def test_parent_path(self) -> None:
        """Test method."""
        result = IssueTemplateConfigFile.I.parent_path()
        assert result == Path(".github/ISSUE_TEMPLATE")

    def test_stem(self) -> None:
        """Test method."""
        assert IssueTemplateConfigFile.I.stem() == "config"
