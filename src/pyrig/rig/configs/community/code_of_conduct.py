"""Configuration management for CODE_OF_CONDUCT.md files.

Manages CODE_OF_CONDUCT.md using the Contributor Covenant, the most widely
adopted code of conduct for open source projects.
"""

from pathlib import Path

from pyrig.core.resources import (
    resource_content,
)
from pyrig.rig import resources
from pyrig.rig.configs.base.markdown import MarkdownConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile


class CodeOfConductConfigFile(MarkdownConfigFile):
    """CODE_OF_CONDUCT.md configuration manager.

    Generates CODE_OF_CONDUCT.md using the Contributor Covenant 3.0 standard.
    Reads the covenant text from a bundled resource file, substitutes the
    project's maintainer email for the reporting placeholder, and strips the
    editorial note that precedes the enforcement ladder.
    """

    def content(self) -> str:
        """Return the completed Contributor Covenant text."""
        return self.code_of_conduct()

    def parent_path(self) -> Path:
        """Return the project root as the parent directory."""
        return Path()

    def stem(self) -> str:
        """Return `"CODE_OF_CONDUCT"` as the filename stem."""
        return "CODE_OF_CONDUCT"

    def code_of_conduct(self) -> str:
        """Return the Contributor Covenant with its placeholders resolved.

        Replaces the reporting placeholder in the covenant text with the
        project's version control email address, and removes the editorial
        note that precedes the enforcement ladder.

        Returns:
            Contributor Covenant 3.0 text with both placeholders resolved.
        """
        return (
            self.code_of_conduct_template()
            .replace(
                self.reporting_placeholder(),
                self.reporting_method(),
                1,
            )
            .replace(
                self.enforcement_placeholder(),
                self.enforcement_method(),
                1,
            )
        )

    def code_of_conduct_template(self) -> str:
        """Return the raw Contributor Covenant 3.0 template text.

        Returns:
            Full covenant text with the reporting and enforcement
            placeholders intact.
        """
        return resource_content("CONTRIBUTOR_COVENANT_CODE_OF_CONDUCT", resources)

    def reporting_method(self) -> str:
        """Return the reporting instructions for the code of conduct.

        Returns:
            A sentence directing reporters to the project's maintainer
            email, e.g. `send an email to <user@example.com>.`.
        """
        return f"send an email to <{PyprojectConfigFile.I.maintainer_email()}>."

    def reporting_placeholder(self) -> str:
        """Return the placeholder for the reporting instructions.

        Returns:
            The `[NOTE: describe your means of reporting here.]` placeholder
            string.
        """
        return "[NOTE: describe your means of reporting here.]"

    def enforcement_method(self) -> str:
        """Return the replacement text for the enforcement editorial note.

        Returns:
            An empty string, so the editorial note is removed rather than
            replaced with alternate text.
        """
        return ""

    def enforcement_placeholder(self) -> str:
        """Return the editorial note that precedes the enforcement ladder.

        Returns:
            The bolded `[NOTE: ...]` note asking maintainers to describe
            their own enforcement policy, surrounded by the blank lines
            that isolate it from the rest of the covenant text.
        """
        return """
**[NOTE: The remedies and repairs outlined below are suggestions based on best
practices in code of conduct enforcement. If your community has its own
established enforcement process, be sure to edit this section to describe your
own policies.]**
"""
