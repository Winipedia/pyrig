"""Configuration management for bug report issue template.

Manages .github/ISSUE_TEMPLATE/bug_report.yml with a minimal bug report template.

See Also:
    pyrig.dev.configs.base.yml.YmlConfigFile
"""

from pathlib import Path
from typing import Any

from pyrig.dev.configs.base.yml import YmlConfigFile


class BugReportConfigFile(YmlConfigFile):
    """Bug report issue template configuration manager.

    Generates .github/ISSUE_TEMPLATE/bug_report.yml with fields for:
    - Description (required)
    - Steps to Reproduce (required)
    - Expected Behavior (required)
    - Actual Behavior (required)
    - Environment (optional)
    - Logs (optional)

    Examples:
        Generate bug_report.yml::

            BugReportConfigFile()

    See Also:
        pyrig.dev.configs.base.yml.YmlConfigFile
    """

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the parent directory for the bug report template.

        Returns:
            Path: .github/ISSUE_TEMPLATE/.
        """
        return Path(".github/ISSUE_TEMPLATE")

    @classmethod
    def _get_configs(cls) -> dict[str, Any]:
        """Get the bug report template configuration.

        Returns:
            dict[str, Any]: Bug report template YAML structure.
        """
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
        """Check if bug_report.yml exists and is non-empty.

        Returns:
            bool: True if file exists with content, False otherwise.
        """
        return cls.get_path().exists() and bool(
            cls.get_path().read_text(encoding="utf-8").strip()
        )
