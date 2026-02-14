"""Manage bug report issue template.

Create .github/ISSUE_TEMPLATE/bug_report.yml with a minimal bug report template.

See Also:
    pyrig.rig.configs.base.yml.YmlConfigFile
"""

from pathlib import Path
from typing import Any

from pyrig.rig.configs.base.yml import YmlConfigFile


class BugReportConfigFile(YmlConfigFile):
    """Manage .github/ISSUE_TEMPLATE/bug_report.yml.

    Bug report template with fields for:
    - Description (required)
    - Steps to Reproduce (required)
    - Expected Behavior (required)
    - Actual Behavior (required)
    - Environment (optional)
    - Logs (optional)

    Example:
        >>> BugReportConfigFile.validate()

    See Also:
        pyrig.rig.configs.base.yml.YmlConfigFile
    """

    @classmethod
    def parent_path(cls) -> Path:
        """Return .github/ISSUE_TEMPLATE/."""
        return Path(".github/ISSUE_TEMPLATE")

    @classmethod
    def _configs(cls) -> dict[str, Any]:
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

    @classmethod
    def is_correct(cls) -> bool:
        """Return True if bug_report.yml exists with content."""
        return cls.path().exists() and bool(
            cls.path().read_text(encoding="utf-8").strip()
        )
