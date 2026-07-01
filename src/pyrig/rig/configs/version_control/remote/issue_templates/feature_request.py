"""Configuration file for the GitHub feature request issue template."""

from pathlib import Path
from typing import Any

from pyrig.rig.configs.base.yml import YMLDictConfigFile


class FeatureRequestConfigFile(YMLDictConfigFile):
    """Config file for `.github/ISSUE_TEMPLATE/feature_request.yml`.

    Generates and validates the GitHub issue form that contributors use to
    submit feature requests. The form guides contributors through describing
    what they want, why they need it, and how it might work.
    """

    def parent_path(self) -> Path:
        """Return the directory containing the feature request template file.

        Returns:
            `Path(".github/ISSUE_TEMPLATE")`.
        """
        return Path(".github/ISSUE_TEMPLATE")

    def stem(self) -> str:
        """Return `"feature_request"` as the filename stem."""
        return "feature_request"

    def _configs(self) -> dict[str, Any]:
        """Return the GitHub issue form definition for feature requests.

        The summary and use case fields are required; the proposed solution
        and alternatives considered fields are optional.

        Returns:
            Issue form metadata (`name`, `description`, `title`, `labels`)
            together with the `body` field definitions.
        """
        return {
            "name": "Feature Request",
            "description": "Suggest a new feature",
            "title": "[Feature]: ",
            "labels": ["enhancement"],
            "body": [
                {
                    "type": "textarea",
                    "id": "summary",
                    "attributes": {
                        "label": "Summary",
                        "description": "Brief explanation of the feature",
                    },
                    "validations": {"required": True},
                },
                {
                    "type": "textarea",
                    "id": "use_case",
                    "attributes": {
                        "label": "Use Case",
                        "description": "Why do you need this feature?",
                    },
                    "validations": {"required": True},
                },
                {
                    "type": "textarea",
                    "id": "proposed",
                    "attributes": {
                        "label": "Proposed Solution",
                        "description": "How might this feature work?",
                    },
                    "validations": {"required": False},
                },
                {
                    "type": "textarea",
                    "id": "alternatives",
                    "attributes": {
                        "label": "Alternatives Considered",
                        "description": "Other solutions you've considered",
                    },
                    "validations": {"required": False},
                },
            ],
        }
