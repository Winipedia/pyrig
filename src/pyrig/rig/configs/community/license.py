"""LICENSE file configuration for generated projects."""

from datetime import UTC, datetime
from pathlib import Path

from spdx_matcher import analyse_license_text

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
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.tools.packages.manager import PackageManager
from pyrig.rig.tools.version_control.controller import VersionController
from pyrig.rig.tools.version_control.remote.controller import (
    RemoteVersionController,
)


class LicenseConfigFile(StringConfigFile):
    """Configuration file management for a project's MIT `LICENSE` file.

    Generates the license text from the current year and repository owner, and
    detects the SPDX license identifier from the file content.
    """

    def content(self) -> str:
        """Return the MIT license text.

        Returns:
            The complete MIT license with year and owner substituted.
        """
        return self.license()

    def extension(self) -> str:
        """Return an empty string — LICENSE has no file extension."""
        return ""

    def extension_separator(self) -> str:
        """Return an empty string — no separator is needed without an extension."""
        return ""

    def parent_path(self) -> Path:
        """Return the project root as the parent directory."""
        return Path()

    def is_correct(self) -> bool:
        """Check whether the LICENSE file has non-empty content.

        Overrides the default content-comparison check with a simpler
        non-emptiness test.

        Returns:
            `True` if the file has non-empty content; `False` if the file
            is empty.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        return file_has_content(self.path())

    def priority(self) -> float:
        """Return a priority one step above `PyprojectConfigFile`'s.

        Ensures this file is validated before `PyprojectConfigFile`
        as it relies on `spdx_identifier()`, which reads the content
        of the LICENSE file on disk.
        """
        return Priority.increase(PyprojectConfigFile.I.priority())

    def stem(self) -> str:
        """Return `'LICENSE'`."""
        return "LICENSE"

    def license(self) -> str:
        """Return the MIT license text with year and repository owner substituted."""
        mit_license = self.license_template()
        year = datetime.now(tz=UTC).year
        owner = VersionController.I.repo_owner()
        mit_license = mit_license.replace(self.year_placeholder(), str(year), 1)
        return mit_license.replace(self.fullname_placeholder(), owner, 1)

    def license_template(self) -> str:
        """Return the raw MIT license template text."""
        return resource_content("MIT_LICENSE", resources)

    def license_badge(self) -> str:
        """Return a Markdown image-link badge for the project license.

        Returns:
            Markdown string in the form
            `[![License](<badge_url>)](<repo_url>/blob/main/LICENSE)`.
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

        Returns:
            URL in the form
            `https://img.shields.io/github/license/<owner>/<repo>`.
        """
        owner, repo = (
            VersionController.I.repo_owner(),
            PackageManager.I.project_name(),
        )
        return f"https://img.shields.io/github/license/{owner}/{repo}"

    def spdx_identifier(self) -> str:
        """Return the SPDX license identifier detected from the LICENSE file content.

        Returns:
            The matched SPDX identifier (e.g., `"MIT"`, `"Apache-2.0"`), or
            `"LicenseRef-Custom"` if no standard license is recognised.
        """
        licenses, _ = analyse_license_text(self.read_content())
        return next(iter(licenses["licenses"]), "LicenseRef-Custom")

    def year_placeholder(self) -> str:
        """Return the placeholder for the year in the license text.

        Returns:
            The `[year]` placeholder string.
        """
        return "[year]"

    def fullname_placeholder(self) -> str:
        """Return the placeholder for the repository owner in the license text.

        Returns:
            The `[fullname]` placeholder string.
        """
        return "[fullname]"
