"""Configuration management for CODE_OF_CONDUCT.md files.

Manages CODE_OF_CONDUCT.md using the Contributor Covenant, the most widely
adopted code of conduct for open source projects.
"""

from functools import cache
from pathlib import Path

from pyrig_runtime.core.wrappers import safe_call

from pyrig.core.network import get_text
from pyrig.core.resources import (
    resource_content,
)
from pyrig.core.strings import file_has_content
from pyrig.rig import resources
from pyrig.rig.configs.base.markdown import MarkdownConfigFile
from pyrig.rig.tools.version_control.version_controller import VersionController


class CodeOfConductConfigFile(MarkdownConfigFile):
    """CODE_OF_CONDUCT.md configuration manager.

    Generates CODE_OF_CONDUCT.md using the Contributor Covenant 2.1 standard.
    Reads the covenant text from a bundled resource file and substitutes the
    project's version control email address for the ``[INSERT CONTACT METHOD]``
    placeholder.
    """

    def stem(self) -> str:
        """Return ``"CODE_OF_CONDUCT"`` as the filename stem."""
        return "CODE_OF_CONDUCT"

    def parent_path(self) -> Path:
        """Return project root as parent directory."""
        return Path()

    def lines(self) -> list[str]:
        """Return the Contributor Covenant content with contact method as lines."""
        return self.split_lines(self.code_of_conduct())

    def is_correct(self) -> bool:
        """Check if CODE_OF_CONDUCT.md has non-empty content.

        Overrides the default content-comparison check with a simpler
        non-emptiness test.

        Returns:
            bool: ``True`` if the file has non-empty content; ``False`` if
            the file is empty.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        return file_has_content(self.path())

    def code_of_conduct(self) -> str:
        """Return the Contributor Covenant with the contact method substituted.

        Replaces the ``[INSERT CONTACT METHOD]`` placeholder in the covenant
        text with the project's version control email address.

        Returns:
            str: Contributor Covenant 2.1 text with the contact method in place.
        """
        return self.code_of_conduct_template().replace(
            "[INSERT CONTACT METHOD]",
            self.contact_method(),
        )

    def code_of_conduct_template(self) -> str:
        """Return the raw Contributor Covenant 2.1 template text.

        Attempts to fetch the latest version from the remote source; falls back
        to the bundled resource if the network is unavailable.

        Returns:
            Full covenant text with the ``[INSERT CONTACT METHOD]`` placeholder intact.
        """
        return safe_call(
            self.remote_code_of_conduct_template,
            default=self.local_code_of_conduct_template(),
        )

    @classmethod
    @cache
    def remote_code_of_conduct_template(cls) -> str:
        """Fetch the Contributor Covenant 2.1 template from the remote source.

        Returns:
            Raw covenant text with the ``[INSERT CONTACT METHOD]`` placeholder intact.
        """
        return get_text(
            "https://raw.githubusercontent.com/github/MVG/main/org-docs/CODE-OF-CONDUCT.md",
        )

    def local_code_of_conduct_template(self) -> str:
        """Return the Contributor Covenant 2.1 template from the bundled resource.

        Returns:
            Raw covenant text with the ``[INSERT CONTACT METHOD]`` placeholder intact.
        """
        return resource_content("CONTRIBUTOR_COVENANT_CODE_OF_CONDUCT", resources)

    def contact_method(self) -> str:
        """Return the contact method for the code of conduct.

        Returns:
            str: Version control email address wrapped in angle brackets,
                e.g., ``<user@example.com>``.
        """
        return f"<{VersionController.I.email()}>"
