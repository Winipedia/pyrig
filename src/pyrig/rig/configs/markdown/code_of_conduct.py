"""Configuration management for CODE_OF_CONDUCT.md files.

Manages CODE_OF_CONDUCT.md using the Contributor Covenant, the most widely
adopted code of conduct for open source projects. Falls back to a bundled
template when the upstream source is unavailable.
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

    Generates CODE_OF_CONDUCT.md using the Contributor Covenant 2.1 standard.
    Reads the covenant text from a bundled resource file and substitutes the
    project's version control email address for the ``[INSERT CONTACT METHOD]``
    placeholder.

    Examples:
        Generate CODE_OF_CONDUCT.md::

            CodeOfConductConfigFile.I.validate()
    """

    def stem(self) -> str:
        """Return ``"CODE_OF_CONDUCT"`` as the filename stem."""
        return "CODE_OF_CONDUCT"

    def parent_path(self) -> Path:
        """Return project root as parent directory."""
        return Path()

    def lines(self) -> list[str]:
        """Return the Contributor Covenant content with contact method as lines."""
        return self.split_lines(self.contributor_covenant_with_contact_method())

    def is_correct(self) -> bool:
        """Check if CODE_OF_CONDUCT.md exists and is non-empty.

        Overrides the default content-comparison check with a simpler
        existence and non-emptiness test. When running inside the pyrig
        development repository, ``contributor_covenant()`` is also called
        to confirm the bundled resource is readable.

        Returns:
            bool: True if the file exists and has non-empty content.
        """
        if src_package_is_pyrig():
            # if in pyrig just run get contributor covenant
            # to trigger resource update if needed
            self.contributor_covenant()
        return self.path().exists() and bool(read_text_utf8(self.path()).strip())

    def contributor_covenant_with_contact_method(self) -> str:
        """Return the Contributor Covenant with the contact method substituted.

        Replaces the ``[INSERT CONTACT METHOD]`` placeholder in the covenant
        text with the project's version control email address.

        Returns:
            str: Contributor Covenant 2.1 text with the contact method in place.
        """
        contact_method = self.contact_method()
        return self.contributor_covenant().replace(
            "[INSERT CONTACT METHOD]", contact_method
        )

    def contributor_covenant(self) -> str:
        """Return the raw Contributor Covenant 2.1 text from the bundled resource.

        Returns:
            str: Full covenant text, unmodified.
        """
        return resource_content("CONTRIBUTOR_COVENANT_CODE_OF_CONDUCT", resources)

    def contact_method(self) -> str:
        """Return the contact method for the code of conduct.

        Returns:
            str: Version control email address wrapped in angle brackets,
                e.g., ``<user@example.com>``.
        """
        return f"<{VersionController.I.email()}>"
