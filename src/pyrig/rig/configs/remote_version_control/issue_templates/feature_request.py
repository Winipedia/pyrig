"""Configuration file for the GitHub feature request issue template."""

from pathlib import Path

from pyrig.core.strings import read_text_utf8
from pyrig.rig.configs.base.config_file import ConfigDict
from pyrig.rig.configs.base.yml import DictYmlConfigFile


class FeatureRequestConfigFile(DictYmlConfigFile):
    """Manages ``.github/ISSUE_TEMPLATE/feature_request.yml``.

    Generates and validates the GitHub issue form that contributors use to
    submit feature requests. The form guides contributors through describing
    what they want, why they need it, and how it might work.

    Example:
        >>> FeatureRequestConfigFile.I.validate()
    """

    def parent_path(self) -> Path:
        """Return the directory containing the feature request template file.

        Returns:
            ``Path(".github/ISSUE_TEMPLATE")``.
        """
        return Path(".github/ISSUE_TEMPLATE")

    def stem(self) -> str:
        """Return ``"feature_request"`` as the filename stem."""
        return "feature_request"

    def _configs(self) -> ConfigDict:
        """Return the GitHub issue form definition for feature requests.

        Defines a form with the following textarea fields:

        - **Summary** (required): A brief description of the requested feature.
        - **Use Case** (required): The motivation or problem the feature would address.
        - **Proposed Solution** (optional): The envisioned way the feature would work.
        - **Alternatives Considered** (optional): Other approaches already evaluated.

        Returns:
            A ``ConfigDict`` representing the full GitHub issue form YAML, including
            metadata such as ``name``, ``description``, ``title``, ``labels``, and
            the ``body`` form fields.
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

    def is_correct(self) -> bool:
        """Return ``True`` if the feature request template file exists and is non-empty.

        Overrides the base class to use a looser correctness check. Rather than
        verifying that all required keys are present, any file with non-whitespace
        content is treated as correct. This allows contributors to freely customize
        the template without the system overwriting their changes.

        Returns:
            ``True`` if the file exists and contains at least one non-whitespace
            character.
        """
        return self.path().exists() and bool(read_text_utf8(self.path()).strip())
