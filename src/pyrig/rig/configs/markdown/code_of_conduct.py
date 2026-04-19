"""Configuration management for CODE_OF_CONDUCT.md files.

Manages CODE_OF_CONDUCT.md using the Contributor Covenant, the most widely
adopted code of conduct for open source projects. Fetches from the official
source with fallback to bundled template.

See Also:
    https://www.contributor-covenant.org/
    pyrig.rig.configs.base.markdown.MarkdownConfigFile
"""

from pathlib import Path

from pyrig.core.introspection.packages import src_package_is_pyrig
from pyrig.core.resources import (
    resource_content,
)
from pyrig.core.strings import read_text_utf8
from pyrig.rig import resources
from pyrig.rig.configs.base.markdown import MarkdownConfigFile
from pyrig.rig.tools.version_controller import VersionController


class CodeOfConductConfigFile(MarkdownConfigFile):
    """CODE_OF_CONDUCT.md configuration manager.

    Generates CODE_OF_CONDUCT.md using the Contributor Covenant 2.1, the most
    widely adopted code of conduct for open source projects. Used by Linux,
    Kubernetes, Rails, Swift, and thousands of other projects.

    Fetches from GitHub's MVG (Minimum Viable Governance) repository with
    fallback to a bundled template. Applicable to both private and public
    repositories.

    Examples:
        Generate CODE_OF_CONDUCT.md::

            CodeOfConductConfigFile.I.validate()

    See Also:
        https://www.contributor-covenant.org/
        pyrig.rig.configs.base.markdown.MarkdownConfigFile
    """

    def stem(self) -> str:
        """Return "CODE_OF_CONDUCT" as the filename."""
        return "CODE_OF_CONDUCT"

    def parent_path(self) -> Path:
        """Return project root as parent directory."""
        return Path()

    def lines(self) -> list[str]:
        """Return Contributor Covenant Code of Conduct content as lines."""
        return self.split_lines(self.contributor_covenant_with_contact_method())

    def is_correct(self) -> bool:
        """Check if CODE_OF_CONDUCT.md exists and is non-empty.

        Note:
            When running inside pyrig itself, this also triggers
            `contributor_covenant()` to update the bundled resource if needed.

        Returns:
            True if file exists with content, False otherwise.
        """
        if src_package_is_pyrig():
            # if in pyrig just run get contributor covenant
            # to trigger resource update if needed
            self.contributor_covenant()
        return self.path().exists() and bool(read_text_utf8(self.path()).strip())

    def contributor_covenant_with_contact_method(self) -> str:
        """Return the Contributor Covenant with the contact method inserted.

        Returns:
            Contributor Covenant 2.1 content with the contact method in place
            of ``[INSERT CONTACT METHOD]``.
        """
        contact_method = self.contact_method()
        return self.contributor_covenant().replace(
            "[INSERT CONTACT METHOD]", contact_method
        )

    def contributor_covenant(self) -> str:
        """Return the Contributor Covenant content from resources."""
        return resource_content("CONTRIBUTOR_COVENANT_CODE_OF_CONDUCT", resources)

    def contact_method(self) -> str:
        """Return the contact method for the code of conduct.

        Returns:
            Version control email wrapped in angle brackets,
            e.g., ``<user@example.com>``.
        """
        return f"<{VersionController.I.email()}>"
