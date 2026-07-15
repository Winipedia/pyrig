"""Test module."""

from pathlib import Path

from pyrig.rig.configs.base.issue_template import IssueTemplateConfigFile
from pyrig.rig.configs.version_control.remote.issue_templates.bug_report import (
    BugReportConfigFile,
)


class TestIssueTemplateConfigFile:
    """Test class."""

    def test_parent_path(self) -> None:
        """Test method."""
        assert issubclass(BugReportConfigFile, IssueTemplateConfigFile)
        assert BugReportConfigFile.I.parent_path() == Path(".github/ISSUE_TEMPLATE")
