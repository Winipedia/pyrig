"""Configuration management for LICENSE files.

This module provides the LicenceConfigFile class for managing the
project's LICENSE file. The file is created empty and users are
expected to add their own license text.
"""

from datetime import UTC, datetime
from pathlib import Path

import requests

from pyrig.dev.configs.base.base import TextConfigFile
from pyrig.dev.utils.resources import return_resource_content_on_fetch_error
from pyrig.src.git.git import get_repo_owner_and_name_from_git


class LicenceConfigFile(TextConfigFile):
    """Configuration file manager for LICENSE.

    Creates an empty LICENSE file in the project root. Users should
    add their preferred license text manually.
    It defaults to the MIT license the file does not exist.
    """

    @classmethod
    def get_filename(cls) -> str:
        """Get the LICENSE filename.

        Returns:
            The string "LICENSE".
        """
        return "LICENSE"

    @classmethod
    def get_path(cls) -> Path:
        """Get the path to the LICENSE file.

        Returns:
            Path to LICENSE in the project root.
        """
        return Path(cls.get_filename())

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the project root directory.

        Returns:
            Path to the project root.
        """
        return Path()

    @classmethod
    def get_file_extension(cls) -> str:
        """Get an empty file extension.

        Returns:
            Empty string (LICENSE has no extension).
        """
        return ""

    @classmethod
    def get_content_str(cls) -> str:
        """Get the initial content (empty).

        Returns:
            Empty string.
        """
        return cls.get_mit_license_with_year_and_owner()

    @classmethod
    def is_correct(cls) -> bool:
        """Check if the LICENSE file is valid.

        Returns:
            True if the file exists and is non-empty.
        """
        return super().is_correct() or (
            cls.get_path().exists()
            and bool(cls.get_path().read_text(encoding="utf-8").strip())
        )

    @classmethod
    @return_resource_content_on_fetch_error(resource_name="MIT_LICENSE_TEMPLATE")
    def get_mit_license(cls) -> str:
        """Get the MIT license text.

        Fetch the MIT license text from GitHub's SPDX license API.
        On exception returns a default MIT license text.

        Returns:
            The MIT license text.
        """
        url = "https://api.github.com/licenses/mit"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        mit_license: str = data["body"]
        return mit_license

    @classmethod
    def get_mit_license_with_year_and_owner(cls) -> str:
        """Get the MIT license text with year and owner.

        Returns:
            The MIT license text with year and owner.
        """
        mit_license = cls.get_mit_license()
        year = datetime.now(tz=UTC).year
        owner, _ = get_repo_owner_and_name_from_git(check_repo_url=False)
        mit_license = mit_license.replace("[year]", str(year))
        return mit_license.replace("[fullname]", owner)
