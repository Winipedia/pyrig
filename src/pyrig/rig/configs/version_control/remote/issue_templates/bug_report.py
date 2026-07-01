"""Configuration file for the GitHub bug report issue template."""

from pathlib import Path
from typing import Any

from pyrig.rig.configs.base.yml import YMLDictConfigFile


class BugReportConfigFile(YMLDictConfigFile):
    """Configuration manager for `.github/ISSUE_TEMPLATE/bug_report.yml`.

    Generates and validates the GitHub issue form contributors use to submit
    bug reports.
    """

    def parent_path(self) -> Path:
        """Return `Path(".github/ISSUE_TEMPLATE")`."""
        return Path(".github/ISSUE_TEMPLATE")

    def stem(self) -> str:
        """Return `"bug_report"` as the filename stem."""
        return "bug_report"

    def _configs(self) -> dict[str, Any]:
        """Return the GitHub issue form definition for bug reports.

        Defines a form with the following textarea fields:

        - **Description** (required): A clear description of the bug.
        - **Steps to Reproduce** (required): Numbered reproduction steps,
          pre-populated with a placeholder list.
        - **Expected Behavior** (required): What the reporter expected to happen.
        - **Actual Behavior** (required): What actually happened.
        - **Environment** (optional): OS, version, and relevant dependencies.
        - **Logs** (optional): Relevant log output, rendered as shell code.

        Returns:
            A `dict[str, Any]` representing the full GitHub issue form YAML,
            including metadata such as `name`, `description`, `title`,
            `labels`, and the `body` form fields.
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
