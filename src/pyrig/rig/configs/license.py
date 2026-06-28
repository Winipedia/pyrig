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

    The LICENSE file must be created before ``PyprojectConfigFile``, which reads
    the license text to auto-detect the SPDX identifier for ``pyproject.toml``.
    This file keeps the default priority; ``PyprojectConfigFile`` enforces the
    ordering by setting its own priority one step below this file's.
    """

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
        """Return the MIT license text as individual lines.

        Returns:
            Lines comprising the complete MIT license with year and owner substituted.
        """
        return self.split_lines(self.license())

    def is_correct(self) -> bool:
        """Check whether the LICENSE file has non-empty content.

        Returns:
            ``True`` if the LICENSE file has non-empty content; ``False`` if
            the file is empty.

        Raises:
            FileNotFoundError: If the LICENSE file does not exist.
        """
        return file_has_content(self.path())

    def license(self) -> str:
        """Return the MIT license text with year and repository owner substituted.

        Returns:
            Complete MIT license text ready to write to the LICENSE file.
        """
        mit_license = self.license_template()
        year = datetime.now(tz=UTC).year
        owner = VersionController.I.repo_owner()
        mit_license = mit_license.replace("[year]", str(year))
        return mit_license.replace("[fullname]", owner)

    def license_template(self) -> str:
        """Return the raw MIT license template text.

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
            image_url=badge_url,
            link_url=f"{repo_url}/blob/main/{self.stem()}",
            alt_text="License",
        )

    def license_badge_url(self) -> str:
        """Return the shields.io badge image URL for the repository license.

        Builds the URL using the repository owner and the project name.

        Returns:
            URL in the form
            ``https://img.shields.io/github/license/<owner>/<repo>``.
        """
        owner, repo = (
            VersionController.I.repo_owner(),
            PackageManager.I.project_name(),
        )
        return f"https://img.shields.io/github/license/{owner}/{repo}"
