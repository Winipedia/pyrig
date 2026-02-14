"""Manage feature request issue template.

Create .github/ISSUE_TEMPLATE/feature_request.yml with a minimal template.

See Also:
    pyrig.rig.configs.base.yml.YmlConfigFile
"""

from pathlib import Path
from typing import Any

from pyrig.rig.configs.base.yml import YmlConfigFile


class FeatureRequestConfigFile(YmlConfigFile):
    """Manage .github/ISSUE_TEMPLATE/feature_request.yml.

    Feature request template with fields for:
    - Summary (required)
    - Use Case (required)
    - Proposed Solution (optional)
    - Alternatives Considered (optional)

    Example:
        >>> FeatureRequestConfigFile.validate()

    See Also:
        pyrig.rig.configs.base.yml.YmlConfigFile
    """

    @classmethod
    def parent_path(cls) -> Path:
        """Return .github/ISSUE_TEMPLATE/."""
        return Path(".github/ISSUE_TEMPLATE")

    @classmethod
    def _configs(cls) -> dict[str, Any]:
        """Return feature request template YAML structure."""
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

    @classmethod
    def is_correct(cls) -> bool:
        """Return True if feature_request.yml exists with content."""
        return cls.path().exists() and bool(
            cls.path().read_text(encoding="utf-8").strip()
        )
