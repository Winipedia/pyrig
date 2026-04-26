"""Manage the GitHub bug report issue template configuration file."""

from pathlib import Path

from pyrig.core.strings import read_text_utf8
from pyrig.rig.configs.base.config_file import ConfigDict
from pyrig.rig.configs.base.yml import DictYmlConfigFile


class BugReportConfigFile(DictYmlConfigFile):
    """Manage ``.github/ISSUE_TEMPLATE/bug_report.yml``.

    Generates and validates the GitHub bug report issue template, which
    provides a structured form for users to submit bug reports. The template
    includes required fields for describing the bug, reproduction steps,
    expected and actual behavior, plus optional fields for environment details
    and log output.

    The file is considered correct as long as it exists with any non-empty
    content, allowing users to freely customize the template after initial
    generation without the system reverting their changes.

    Example:
        >>> BugReportConfigFile.I.validate()
    """

    def parent_path(self) -> Path:
        """Return the directory that contains the bug report template.

        Returns:
            Path to ``.github/ISSUE_TEMPLATE``, relative to the project root.
        """
        return Path(".github/ISSUE_TEMPLATE")

    def stem(self) -> str:
        """Return the filename stem for the bug report template file.

        Returns:
            ``"bug_report"``, which combined with the ``.yml`` extension
            produces ``bug_report.yml``.
        """
        return "bug_report"

    def _configs(self) -> ConfigDict:
        """Return the complete YAML structure for the bug report issue template.

        Defines the GitHub issue form with six textarea fields that guide the
        reporter through a structured bug report:

        - **Description** (required): A clear description of the bug.
        - **Steps to Reproduce** (required): Numbered reproduction steps,
          pre-populated with a placeholder list.
        - **Expected Behavior** (required): What the reporter expected to happen.
        - **Actual Behavior** (required): What actually happened.
        - **Environment** (optional): OS, version, and relevant dependencies.
        - **Logs** (optional): Relevant log output, rendered as shell code.

        Returns:
            A ``ConfigDict`` containing the full GitHub issue form schema.
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

    def is_correct(self) -> bool:
        """Return whether the bug report template file exists with content.

        Overrides the base class check, which verifies that all required config
        keys are present. For issue templates, any non-empty file is treated as
        correct, so that user customizations are preserved and never overwritten
        by the system.

        Returns:
            ``True`` if the file exists and contains at least one non-whitespace
            character; ``False`` otherwise.
        """
        return self.path().exists() and bool(read_text_utf8(self.path()).strip())
