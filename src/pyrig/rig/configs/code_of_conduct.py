"""Configuration management for CODE_OF_CONDUCT.md files.

Manages CODE_OF_CONDUCT.md using the Contributor Covenant, the most widely
adopted code of conduct for open source projects.
"""

from pathlib import Path

from pyrig.core.resources import (
    resource_content,
)
from pyrig.core.strings import file_has_content
from pyrig.rig import resources
from pyrig.rig.configs.base.markdown import MarkdownConfigFile
from pyrig.rig.tools.version_control.controller import VersionController


class CodeOfConductConfigFile(MarkdownConfigFile):
    """CODE_OF_CONDUCT.md configuration manager.

    Generates CODE_OF_CONDUCT.md using the Contributor Covenant 2.1 standard.
    Reads the covenant text from a bundled resource file and substitutes the
    project's version control email address for the `[INSERT CONTACT METHOD]`
    placeholder.
    """

    def is_correct(self) -> bool:
        """Check whether CODE_OF_CONDUCT.md has non-empty content.

        Overrides the default content-comparison check with a simpler
        non-emptiness test.

        Returns:
            `True` if the file has non-empty content; `False` if the file
            is empty.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        return file_has_content(self.path())

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
        """Return the Contributor Covenant with the contact method substituted.

        Replaces the `[INSERT CONTACT METHOD]` placeholder in the covenant
        text with the project's version control email address.

        Returns:
            Contributor Covenant 2.1 text with the contact method in place.
        """
        return self.code_of_conduct_template().replace(
            "[INSERT CONTACT METHOD]",
            self.contact_method(),
            1,
        )

    def code_of_conduct_template(self) -> str:
        """Return the raw Contributor Covenant 2.1 template text.

        Returns:
            Full covenant text with the `[INSERT CONTACT METHOD]` placeholder intact.
        """
        return resource_content("CONTRIBUTOR_COVENANT_CODE_OF_CONDUCT", resources)

    def contact_method(self) -> str:
        """Return the contact method for the code of conduct.

        Returns:
            Version control email address wrapped in angle brackets, e.g.
            `<user@example.com>`.
        """
        return f"<{VersionController.I.email()}>"
