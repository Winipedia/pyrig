"""module."""

from pathlib import Path

from pyrig.dev.configs.issue_templates.bug_report import BugReportConfigFile


class TestBugReportConfigFile:
    """Test class."""

    def test_get_parent_path(self) -> None:
        """Test method."""
        result = BugReportConfigFile.get_parent_path()
        assert result == Path(".github/ISSUE_TEMPLATE")

    def test__get_configs(self) -> None:
        """Test method."""
        result = BugReportConfigFile._get_configs()  # noqa: SLF001
        assert isinstance(result, dict)

    def test_is_correct(self) -> None:
        """Test method."""
        assert BugReportConfigFile().is_correct()
