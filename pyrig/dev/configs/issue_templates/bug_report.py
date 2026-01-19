"""Configuration management for bug report issue template.

Manages .github/ISSUE_TEMPLATE/bug_report.yml with a minimal bug report template.

See Also:
    https://github.com/stevemao/github-issue-templates
    pyrig.dev.configs.base.yml.YmlConfigFile
"""

from pathlib import Path
from typing import Any

from pyrig.dev.configs.base.yml import YmlConfigFile


class BugReportConfigFile(YmlConfigFile):
    """Bug report issue template configuration manager.

    Generates .github/ISSUE_TEMPLATE/bug_report.yml with fields for:
    - Description (required)
    - Reproduction steps (required)
    - Expected behavior (required)
    - Environment (optional)
    - Logs (optional)

    Examples:
        Generate bug_report.yml::

            BugReportConfigFile()

    See Also:
        https://github.com/stevemao/github-issue-templates
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
            "description": "Create a new ticket for a bug.",
            "title": "[BUG] - <title>",
            "labels": ["bug"],
            "body": [
                {
                    "type": "textarea",
                    "id": "description",
                    "attributes": {
                        "label": "Description",
                        "description": "Please enter an explicit description of your issue",  # noqa: E501
                        "placeholder": "Short and explicit description of your incident...",  # noqa: E501
                    },
                    "validations": {"required": True},
                },
                {
                    "type": "input",
                    "id": "reprod-url",
                    "attributes": {
                        "label": "Reproduction URL",
                        "description": (
                            "Please enter your GitHub URL to provide a reproduction of the issue"  # noqa: E501
                        ),
                        "placeholder": "ex. https://github.com/USERNAME/REPO-NAME",
                    },
                    "validations": {"required": True},
                },
                {
                    "type": "textarea",
                    "id": "reprod",
                    "attributes": {
                        "label": "Reproduction steps",
                        "description": "Please enter an explicit description of your issue",  # noqa: E501
                        "value": (
                            "1. Go to '...'\n\n"
                            "2. Click on '....'\n\n"
                            "3. Scroll down to '....'\n\n"
                            "4. See error\n"
                        ),
                        "render": "bash",
                    },
                    "validations": {"required": True},
                },
                {
                    "type": "textarea",
                    "id": "screenshot",
                    "attributes": {
                        "label": "Screenshots",
                        "description": (
                            "If applicable, add screenshots to help explain your problem."  # noqa: E501
                        ),
                        "value": "![DESCRIPTION](LINK.png)\n",
                        "render": "bash",
                    },
                    "validations": {"required": False},
                },
                {
                    "type": "textarea",
                    "id": "logs",
                    "attributes": {
                        "label": "Logs",
                        "description": "Please copy and paste any relevant log output. This will be automatically formatted into code, so no need for backticks.",  # noqa: E501
                        "render": "bash",
                    },
                    "validations": {"required": False},
                },
                {
                    "type": "dropdown",
                    "id": "browsers",
                    "attributes": {
                        "label": "Browsers",
                        "description": "What browsers are you seeing the problem on ?",
                        "multiple": True,
                        "options": [
                            "Firefox",
                            "Chrome",
                            "Safari",
                            "Microsoft Edge",
                            "Opera",
                        ],
                    },
                    "validations": {"required": False},
                },
                {
                    "type": "dropdown",
                    "id": "os",
                    "attributes": {
                        "label": "OS",
                        "description": "What is the impacted environment ?",
                        "multiple": True,
                        "options": ["Windows", "Linux", "Mac"],
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
