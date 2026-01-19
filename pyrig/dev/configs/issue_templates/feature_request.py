"""Configuration management for feature request issue template.

Manages .github/ISSUE_TEMPLATE/feature_request.yml
with a minimal feature request template.

See Also:
    https://github.com/stevemao/github-issue-templates
    pyrig.dev.configs.base.yml.YmlConfigFile
"""

from pathlib import Path
from typing import Any

from pyrig.dev.configs.base.yml import YmlConfigFile


class FeatureRequestConfigFile(YmlConfigFile):
    """Feature request issue template configuration manager.

    Generates .github/ISSUE_TEMPLATE/feature_request.yml with fields for:
    - Summary (required)
    - Use case (required)
    - Proposed solution (optional)
    - Alternatives considered (optional)

    Examples:
        Generate feature_request.yml::

            FeatureRequestConfigFile()

    See Also:
        https://github.com/stevemao/github-issue-templates
        pyrig.dev.configs.base.yml.YmlConfigFile
    """

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the parent directory for the feature request template.

        Returns:
            Path: .github/ISSUE_TEMPLATE/.
        """
        return Path(".github/ISSUE_TEMPLATE")

    @classmethod
    def _get_configs(cls) -> dict[str, Any]:
        """Get the feature request template configuration.

        Returns:
            dict[str, Any]: Feature request template YAML structure.
        """
        return {
            "name": "Feature Request",
            "description": "Create a new ticket for a new feature request",
            "title": "[REQUEST] - <title>",
            "labels": ["question"],
            "body": [
                {
                    "type": "input",
                    "id": "start_date",
                    "attributes": {
                        "label": "Start Date",
                        "description": "Start of development",
                        "placeholder": "month/day/year",
                    },
                    "validations": {"required": False},
                },
                {
                    "type": "textarea",
                    "id": "implementation_pr",
                    "attributes": {
                        "label": "Implementation PR",
                        "description": "Pull request used",
                        "placeholder": "#Pull Request ID",
                    },
                    "validations": {"required": False},
                },
                {
                    "type": "textarea",
                    "id": "reference_issues",
                    "attributes": {
                        "label": "Reference Issues",
                        "description": "Common issues",
                        "placeholder": "#Issues IDs",
                    },
                    "validations": {"required": False},
                },
                {
                    "type": "textarea",
                    "id": "summary",
                    "attributes": {
                        "label": "Summary",
                        "description": "Provide a brief explanation of the feature",
                        "placeholder": "Describe in a few lines your feature request",
                    },
                    "validations": {"required": True},
                },
                {
                    "type": "textarea",
                    "id": "basic_example",
                    "attributes": {
                        "label": "Basic Example",
                        "description": "Indicate here some basic examples of your feature.",  # noqa: E501
                        "placeholder": "A few specific words about your feature request.",  # noqa: E501
                    },
                    "validations": {"required": True},
                },
                {
                    "type": "textarea",
                    "id": "drawbacks",
                    "attributes": {
                        "label": "Drawbacks",
                        "description": "What are the drawbacks/impacts of your feature request ?",  # noqa: E501
                        "placeholder": (
                            "Identify the drawbacks and impacts while being neutral on your "  # noqa: E501
                            "feature request"
                        ),
                    },
                    "validations": {"required": True},
                },
                {
                    "type": "textarea",
                    "id": "unresolved_question",
                    "attributes": {
                        "label": "Unresolved questions",
                        "description": "What questions still remain unresolved ?",
                        "placeholder": "Identify any unresolved issues.",
                    },
                    "validations": {"required": False},
                },
            ],
        }

    @classmethod
    def is_correct(cls) -> bool:
        """Check if feature_request.yml exists and is non-empty.

        Returns:
            bool: True if file exists with content, False otherwise.
        """
        return cls.get_path().exists() and bool(
            cls.get_path().read_text(encoding="utf-8").strip()
        )
