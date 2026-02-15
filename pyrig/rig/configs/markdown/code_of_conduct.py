"""Configuration management for CODE_OF_CONDUCT.md files.

Manages CODE_OF_CONDUCT.md using the Contributor Covenant, the most widely
adopted code of conduct for open source projects. Fetches from the official
source with fallback to bundled template.

See Also:
    https://www.contributor-covenant.org/
    pyrig.rig.configs.base.markdown.MarkdownConfigFile
"""

from pathlib import Path

import requests

from pyrig.rig.configs.base.markdown import MarkdownConfigFile
from pyrig.rig.tools.version_controller import VersionController
from pyrig.rig.utils.packages import src_package_is_pyrig
from pyrig.rig.utils.resources import return_resource_content_on_fetch_error


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

    def filename(self) -> str:
        """Return "CODE_OF_CONDUCT" as the filename."""
        return "CODE_OF_CONDUCT"

    def parent_path(self) -> Path:
        """Return project root as parent directory."""
        return Path()

    def lines(self) -> list[str]:
        """Return Contributor Covenant Code of Conduct content as lines."""
        return [*self.contributor_covenant_with_contact_method().splitlines()]

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
        return self.path().exists() and bool(
            self.path().read_text(encoding="utf-8").strip()
        )

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

    @return_resource_content_on_fetch_error(
        resource_name="CONTRIBUTOR_COVENANT_CODE_OF_CONDUCT.md"
    )
    def contributor_covenant(self) -> str:
        """Fetch the Contributor Covenant from GitHub's MVG repository.

        Fall back to a bundled resource template on fetch error.

        Returns:
            Contributor Covenant 2.1 content.
        """
        resp = requests.get(
            "https://raw.githubusercontent.com/github/MVG/main/org-docs/CODE-OF-CONDUCT.md",
            timeout=10,
        )
        resp.raise_for_status()
        return resp.text

    def contact_method(self) -> str:
        """Return the contact method for the code of conduct.

        Returns:
            Version control email wrapped in angle brackets,
            e.g., ``<user@example.com>``.
        """
        return f"<{VersionController.I.email()}>"
