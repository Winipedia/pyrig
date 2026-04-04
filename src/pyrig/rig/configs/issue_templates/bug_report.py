"""Manage bug report issue template.

Create .github/ISSUE_TEMPLATE/bug_report.yml with a minimal bug report template.

See Also:
    pyrig.rig.configs.base.yml.YmlConfigFile
"""

from pathlib import Path

from pyrig.rig.configs.base.base import ConfigDict
from pyrig.rig.configs.base.yml import DictYmlConfigFile


class BugReportConfigFile(DictYmlConfigFile):
    """Manage .github/ISSUE_TEMPLATE/bug_report.yml.

    Bug report template with fields for:
    - Description (required)
    - Steps to Reproduce (required)
    - Expected Behavior (required)
    - Actual Behavior (required)
    - Environment (optional)
    - Logs (optional)

    Example:
        >>> BugReportConfigFile.I.validate()

    See Also:
        pyrig.rig.configs.base.yml.YmlConfigFile
    """

    def parent_path(self) -> Path:
        """Return .github/ISSUE_TEMPLATE/."""
        return Path(".github/ISSUE_TEMPLATE")

    def _configs(self) -> ConfigDict:
        """Return bug report template YAML structure."""
        return {
            "name": "Bug Report",
            "description": "Report a bug",
            "title": "[Bug]: ",
            "labels": ["bug"],
            "body": [
                {
                    "type": "textarea",
                    "id": "description",
                    "attributes": {
                        "label": "Description",
                        "description": "A clear description of the bug",
                    },
                    "validations": {"required": True},
                },
                {
                    "type": "textarea",
                    "id": "steps",
                    "attributes": {
                        "label": "Steps to Reproduce",
                        "value": "1. \n2. \n3. \n",
                    },
                    "validations": {"required": True},
                },
                {
                    "type": "textarea",
                    "id": "expected",
                    "attributes": {
                        "label": "Expected Behavior",
                    },
                    "validations": {"required": True},
                },
                {
                    "type": "textarea",
                    "id": "actual",
                    "attributes": {
                        "label": "Actual Behavior",
                    },
                    "validations": {"required": True},
                },
                {
                    "type": "textarea",
                    "id": "environment",
                    "attributes": {
                        "label": "Environment",
                        "description": "OS, version, relevant dependencies",
                    },
                    "validations": {"required": False},
                },
                {
                    "type": "textarea",
                    "id": "logs",
                    "attributes": {
                        "label": "Logs",
                        "description": "Relevant log output (auto-formatted as code)",
                        "render": "shell",
                    },
                    "validations": {"required": False},
                },
            ],
        }

    def is_correct(self) -> bool:
        """Return True if bug_report.yml exists with content."""
        return self.path().exists() and bool(
            self.path().read_text(encoding="utf-8").strip()
        )
