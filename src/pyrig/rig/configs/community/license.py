"""Configuration management for LICENSE files.

Manages the LICENSE file's content and exposes its detected SPDX license
identifier.
"""

import re
from datetime import UTC, datetime
from functools import cache
from pathlib import Path

from pyrig_runtime.core.strings import regex_find
from pyrig_runtime.core.wrappers import safe_call
from spdx_matcher import analyse_license_text

from pyrig.core.resources import (
    resource_content,
)
from pyrig.core.strings import (
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

    Generates the license text from the repository owner and the year
    already recorded in an existing `LICENSE` file (or the current year if
    no year was found), detects the SPDX license identifier from
    the file's current content, and provides a shields.io license badge for
    use in other generated files.
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
        year = safe_call(
            lambda: regex_find(
                re.compile(r"Copyright \(c\) (\d{4})"),
                self.read_content(),
            ),
            exceptions=(FileNotFoundError, LookupError),
            default=str(datetime.now(tz=UTC).astimezone().year),
        )
        return (
            self.license_template()
            .replace(
                self.year_placeholder(),
                year,
                1,
            )
            .replace(self.fullname_placeholder(), VersionController.I.repo_owner(), 1)
        )

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

    @classmethod
    @cache
    def spdx_identifier(cls) -> str:
        """Return the SPDX license identifier detected from the LICENSE file content.

        The result is cached per class and is not recomputed if the file
        content changes afterward.

        Returns:
            The matched SPDX identifier (e.g., `"MIT"`, `"Apache-2.0"`), or
            `"LicenseRef-Custom"` if no standard license is recognized.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        licenses, _ = analyse_license_text(cls().read_content())
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
