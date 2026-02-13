"""Configuration management for CODE_OF_CONDUCT.md files.

Manages CODE_OF_CONDUCT.md using the Contributor Covenant, the most widely
adopted code of conduct for open source projects. Fetches from the official
source with fallback to bundled template.

See Also:
    https://www.contributor-covenant.org/
    pyrig.rig.configs.base.markdown.MarkdownConfigFile
"""

from functools import cache
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

            CodeOfConductConfigFile()

    See Also:
        https://www.contributor-covenant.org/
        pyrig.rig.configs.base.markdown.MarkdownConfigFile
    """

    @classmethod
    def filename(cls) -> str:
        """Get the CODE_OF_CONDUCT filename.

        Returns:
            str: "CODE_OF_CONDUCT" (extension added by parent).
        """
        return "CODE_OF_CONDUCT"

    @classmethod
    def parent_path(cls) -> Path:
        """Get the parent directory for CODE_OF_CONDUCT.md.

        Returns:
            Path: Project root.
        """
        return Path()

    @classmethod
    def lines(cls) -> list[str]:
        """Get the Contributor Covenant Code of Conduct content.

        Returns:
            list[str]: Contributor Covenant 2.1 lines.
        """
        return [*cls.contributor_covenant_with_contact_method().splitlines()]

    @classmethod
    def is_correct(cls) -> bool:
        """Check if CODE_OF_CONDUCT.md exists and is non-empty.

        Returns:
            bool: True if file exists with content, False otherwise.
        """
        if src_package_is_pyrig():
            # if in pyrig just run get contributor covenant
            # to trigger resource update if needed
            cls.contributor_covenant()
        return cls.path().exists() and bool(
            cls.path().read_text(encoding="utf-8").strip()
        )

    @classmethod
    def contributor_covenant_with_contact_method(cls) -> str:
        """Get the Contributor Covenant with the contact method.

        Returns:
            str: Contributor Covenant 2.1 content with contact method inserted
                in place of [INSERT CONTACT METHOD].
        """
        contact_method = cls.contact_method()
        return cls.contributor_covenant().replace(
            "[INSERT CONTACT METHOD]", contact_method
        )

    @classmethod
    @cache
    @return_resource_content_on_fetch_error(
        resource_name="CONTRIBUTOR_COVENANT_CODE_OF_CONDUCT.md"
    )
    def contributor_covenant(cls) -> str:
        """Fetch Contributor Covenant from GitHub MVG (with fallback).

        Returns:
            str: Contributor Covenant 2.1 content.
        """
        resp = requests.get(
            "https://raw.githubusercontent.com/github/MVG/main/org-docs/CODE-OF-CONDUCT.md",
            timeout=10,
        )
        resp.raise_for_status()
        return resp.text

    @classmethod
    def contact_method(cls) -> str:
        """Get the contact method for the code of conduct.

        Returns:
            str: The email in the version control, e.g. the email in git config
        """
        return f"<{VersionController.I.email()}>"
