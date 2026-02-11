"""Manages LICENSE files.

Creates LICENSE with MIT license (current year + repo owner from git).
Fetches from GitHub SPDX API with fallback template. Users can replace with
preferred license. License type auto-detected for pyproject.toml.

See Also:
    https://api.github.com/licenses
    https://spdx.org/licenses/
"""

from datetime import UTC, datetime
from functools import cache
from pathlib import Path

import requests

from pyrig.rig.configs.base.base import Priority
from pyrig.rig.configs.base.string_ import StringConfigFile
from pyrig.rig.tools.remote_version_controller import RemoteVersionController
from pyrig.rig.tools.version_controller import VersionController
from pyrig.rig.utils.resources import return_resource_content_on_fetch_error


class LicenseConfigFile(StringConfigFile):
    """Manages LICENSE files with MIT license (year + owner from git).

    Fetches from GitHub SPDX API with fallback. Priority 30 (created early
    for pyproject.toml license detection).

    See Also:
        pyrig.rig.configs.pyproject.PyprojectConfigFile.L.detect_project_license
    """

    @classmethod
    def get_priority(cls) -> float:
        """Return priority 30 (created early for pyproject.toml license detection)."""
        return Priority.HIGH

    @classmethod
    def get_filename(cls) -> str:
        """Return 'LICENSE'."""
        return "LICENSE"

    @classmethod
    def get_path(cls) -> Path:
        """Return path to LICENSE in project root."""
        return Path(cls.get_filename())

    @classmethod
    def get_parent_path(cls) -> Path:
        """Return project root."""
        return Path()

    @classmethod
    def get_file_extension(cls) -> str:
        """Return empty string (no extension)."""
        return ""

    @classmethod
    def get_lines(cls) -> list[str]:
        """Get MIT license with year and owner."""
        return cls.get_mit_license_with_year_and_owner().splitlines()

    @classmethod
    def is_correct(cls) -> bool:
        """Check if LICENSE exists and is non-empty."""
        return cls.get_path().exists() and bool(
            cls.get_path().read_text(encoding="utf-8").strip()
        )

    @classmethod
    @cache
    @return_resource_content_on_fetch_error(resource_name="MIT_LICENSE_TEMPLATE")
    def get_mit_license(cls) -> str:
        """Fetch MIT license from GitHub SPDX API (with fallback)."""
        url = "https://api.github.com/licenses/mit"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        mit_license: str = data["body"]
        return mit_license

    @classmethod
    def get_mit_license_with_year_and_owner(cls) -> str:
        """Get MIT license with year and owner from git."""
        mit_license = cls.get_mit_license()
        year = datetime.now(tz=UTC).year
        owner, _ = VersionController.L.get_repo_owner_and_name(check_repo_url=False)
        mit_license = mit_license.replace("[year]", str(year))
        return mit_license.replace("[fullname]", owner)

    @classmethod
    def get_license_badge_url(cls) -> str:
        """Construct GitHub license badge URL.

        Returns:
            shields.io badge URL showing repository license.
        """
        owner, repo = VersionController.L.get_repo_owner_and_name(
            check_repo_url=False,
            url_encode=True,
        )
        return f"https://img.shields.io/github/license/{owner}/{repo}"

    @classmethod
    def get_license_badge(cls) -> str:
        """Construct GitHub license badge Markdown string.

        Returns:
            Markdown string for shields.io badge showing repository license.
        """
        badge_url = cls.get_license_badge_url()
        repo_url = RemoteVersionController.L.get_repo_url()
        return rf"[![License]({badge_url})]({repo_url}/blob/main/LICENSE)"
