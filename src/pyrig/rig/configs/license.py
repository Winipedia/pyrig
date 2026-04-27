"""LICENSE file configuration for generated projects."""

from datetime import UTC, datetime
from pathlib import Path

from pyrig.core.resources import (
    resource_content,
)
from pyrig.core.strings import (
    file_has_content,
    make_linked_badge_markdown,
)
from pyrig.rig import resources
from pyrig.rig.configs.base.config_file import Priority
from pyrig.rig.configs.base.string_ import StringConfigFile
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.version_control.remote import (
    RemoteVersionController,
)
from pyrig.rig.tools.version_control.version_controller import VersionController


class LicenseConfigFile(StringConfigFile):
    """Manages the ``LICENSE`` file for a project using the MIT license.

    Generates the LICENSE file by loading the MIT license template from the
    bundled resources and substituting the current year and the repository
    owner derived from git. The file is placed at the project root with no
    extension.

    Uses ``Priority.HIGH`` so the LICENSE file is created before
    ``PyprojectConfigFile``, which reads the license text to auto-detect the
    SPDX identifier for ``pyproject.toml``.
    """

    def priority(self) -> float:
        """Return ``Priority.HIGH`` to ensure early creation.

        The LICENSE file must exist before ``PyprojectConfigFile`` is
        validated, because ``PyprojectConfigFile.detect_project_license``
        reads the LICENSE content to determine the SPDX identifier written
        into ``pyproject.toml``.

        Returns:
            ``Priority.HIGH``
        """
        return Priority.HIGH

    def stem(self) -> str:
        """Return ``'LICENSE'``."""
        return "LICENSE"

    def parent_path(self) -> Path:
        """Return the project root as the parent directory."""
        return Path()

    def extension(self) -> str:
        """Return an empty string — LICENSE has no file extension."""
        return ""

    def extension_separator(self) -> str:
        """Return an empty string — no separator is needed without an extension."""
        return ""

    def lines(self) -> list[str]:
        """Return the MIT license text split into individual lines.

        Delegates to ``mit_license_with_year_and_owner`` to produce the full
        license text, then splits it into lines for the ``StringConfigFile``
        base-class validation.

        Returns:
            List of lines comprising the MIT license with year and owner
            already substituted.
        """
        return self.split_lines(self.mit_license_with_year_and_owner())

    def is_correct(self) -> bool:
        """Check whether the LICENSE file has non-empty content.

        Returns:
            ``True`` if the LICENSE file has non-empty content; ``False`` if
            the file is empty.

        Raises:
            FileNotFoundError: If the LICENSE file does not exist.
        """
        return file_has_content(self.path())

    def mit_license_with_year_and_owner(self) -> str:
        """Return the MIT license text with year and owner substituted.

        Loads the raw template via ``mit_license`` and replaces the ``[year]``
        placeholder with the current UTC year and the ``[fullname]`` placeholder
        with the repository owner parsed from the git remote URL (or the git
        username when no remote is configured).

        Returns:
            Complete MIT license text ready to write to the LICENSE file.
        """
        mit_license = self.mit_license()
        year = datetime.now(tz=UTC).year
        owner = VersionController.I.repo_owner(check_repo_url=False)
        mit_license = mit_license.replace("[year]", str(year))
        return mit_license.replace("[fullname]", owner)

    def mit_license(self) -> str:
        """Return the raw MIT license template from the bundled resources.

        The template contains ``[year]`` and ``[fullname]`` placeholders that
        are filled in by ``mit_license_with_year_and_owner``.

        Returns:
            Raw MIT license template text.
        """
        return resource_content("MIT_LICENSE", resources)

    def license_badge(self) -> str:
        """Return a Markdown image-link badge for the project license.

        Combines the shields.io badge image from ``license_badge_url`` with
        a link to the ``LICENSE`` file on the repository's main branch.
        Used when generating the project's README badges section.

        Returns:
            Markdown string in the form
            ``[![License](<badge_url>)](<repo_url>/blob/main/LICENSE)``.
        """
        badge_url = self.license_badge_url()
        repo_url = RemoteVersionController.I.repo_url()
        return make_linked_badge_markdown(
            badge_url=badge_url,
            link_url=f"{repo_url}/blob/main/{self.stem()}",
            alt_text="License",
        )

    def license_badge_url(self) -> str:
        """Return the shields.io badge image URL for the repository license.

        Builds the URL using the percent-encoded repository owner and name so
        the URL is safe for embedding in Markdown.

        Returns:
            URL in the form
            ``https://img.shields.io/github/license/<owner>/<repo>``.
        """
        owner, repo = (
            VersionController.I.repo_owner(
                check_repo_url=False,
                url_encode=True,
            ),
            PackageManager.I.project_name(),
        )
        return f"https://img.shields.io/github/license/{owner}/{repo}"
