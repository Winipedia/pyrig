"""Manage LICENSE files.

Creates LICENSE with MIT license (current year + repo owner from git).
Fetches from GitHub SPDX API with fallback template. Users can replace with
preferred license. License type auto-detected for pyproject.toml.

See Also:
    https://api.github.com/licenses
    https://spdx.org/licenses/
"""

from datetime import UTC, datetime
from pathlib import Path

from pyrig.core.resource import (
    resource_content,
)
from pyrig.core.string_ import make_linked_badge_markdown
from pyrig.rig import resources
from pyrig.rig.configs.base.config_file import Priority
from pyrig.rig.configs.base.string_ import StringConfigFile
from pyrig.rig.tools.remote_version_controller import RemoteVersionController
from pyrig.rig.tools.version_controller import VersionController
from pyrig.rig.utils.packages import src_package_is_pyrig


class LicenseConfigFile(StringConfigFile):
    """Manage LICENSE files with MIT license (year + owner from git).

    Fetch from GitHub SPDX API with fallback. `Priority.HIGH` (created early
    for pyproject.toml license detection).

    See Also:
        pyrig.rig.configs.pyproject.PyprojectConfigFile.I.detect_project_license
    """

    def priority(self) -> float:
        """Return `Priority.HIGH`.

        Is created early for pyproject.toml license detection.
        """
        return Priority.HIGH

    def stem(self) -> str:
        """Return 'LICENSE'."""
        return "LICENSE"

    def parent_path(self) -> Path:
        """Return project root."""
        return Path()

    def extension(self) -> str:
        """Return empty string (no extension)."""
        return ""

    def extension_separator(self) -> str:
        """Return empty string (no extension separator)."""
        return ""

    def lines(self) -> list[str]:
        """Get MIT license with year and owner."""
        return self.split_lines(self.mit_license_with_year_and_owner())

    def is_correct(self) -> bool:
        """Check if LICENSE exists and is non-empty."""
        if src_package_is_pyrig():
            # if in pyrig just run get mit licence to trigger resource update if needed
            self.mit_license()
        return self.path().exists() and bool(
            self.path().read_text(encoding="utf-8").strip()
        )

    def mit_license(self) -> str:
        """Get MIT license template from the resources."""
        return resource_content("MIT_LICENSE", resources)

    def mit_license_with_year_and_owner(self) -> str:
        """Get MIT license with year and owner from git."""
        mit_license = self.mit_license()
        year = datetime.now(tz=UTC).year
        owner, _ = VersionController.I.repo_owner_and_name(check_repo_url=False)
        mit_license = mit_license.replace("[year]", str(year))
        return mit_license.replace("[fullname]", owner)

    def license_badge_url(self) -> str:
        """Construct a shields.io badge URL for the repository license."""
        owner, repo = VersionController.I.repo_owner_and_name(
            check_repo_url=False,
            url_encode=True,
        )
        return f"https://img.shields.io/github/license/{owner}/{repo}"

    def license_badge(self) -> str:
        """Construct a shields.io license badge as a Markdown image link."""
        badge_url = self.license_badge_url()
        repo_url = RemoteVersionController.I.repo_url()
        return make_linked_badge_markdown(
            badge_url=badge_url,
            link_url=f"{repo_url}/blob/main/{self.stem()}",
            alt_text="License",
        )
