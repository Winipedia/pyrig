"""Configuration management for LICENSE files.

This module provides the LicenceConfigFile class for managing the project's
LICENSE file. By default, it creates a LICENSE file with the MIT license text,
automatically filled with the current year and repository owner.

The MIT license is fetched from GitHub's SPDX license API. If the API is
unavailable, a fallback MIT license template from resources is used.

Users can replace the LICENSE file content with their preferred license text
after initialization. The license type is automatically detected from the
LICENSE file content and included in pyproject.toml.

See Also:
    GitHub SPDX License API: https://api.github.com/licenses
    SPDX License List: https://spdx.org/licenses/
"""

from datetime import UTC, datetime
from pathlib import Path

import requests

from pyrig.dev.configs.base.text import TextConfigFile
from pyrig.dev.utils.resources import return_resource_content_on_fetch_error
from pyrig.src.git import get_repo_owner_and_name_from_git


class LicenceConfigFile(TextConfigFile):
    """Configuration file manager for LICENSE files.

    Creates a LICENSE file in the project root with the MIT license text by
    default. The license is automatically populated with the current year and
    repository owner extracted from git configuration.

    The MIT license text is fetched from GitHub's SPDX license API. If the API
    is unavailable, a fallback template from resources is used. Users can
    replace the content with their preferred license after initialization.

    This config file has priority 30, ensuring it's created early so that
    pyproject.toml can detect and include the license type.

    Examples:
        Initialize the LICENSE file::

            from pyrig.dev.configs.licence import LicenceConfigFile

            # Creates LICENSE with MIT license
            LicenceConfigFile()

        The generated LICENSE will contain::

            MIT License

            Copyright (c) 2025 username

            Permission is hereby granted, free of charge, ...

    Note:
        This method makes an external API call to GitHub to fetch the MIT
        license template. On failure, it uses a fallback template from
        resources.

    See Also:
        pyrig.dev.configs.pyproject.PyprojectConfigFile.detect_project_licence
            Method that reads the LICENSE file to detect license type
    """

    @classmethod
    def get_priority(cls) -> float:
        """Get the initialization priority for this config file.

        Returns:
            float: Priority value of 30. Higher values are initialized first.
                This file has elevated priority because pyproject.toml needs
                to read the LICENSE file to detect the license type.
        """
        return 30

    @classmethod
    def get_filename(cls) -> str:
        """Get the LICENSE filename.

        Returns:
            str: The string "LICENSE" (uppercase, no extension).
        """
        return "LICENSE"

    @classmethod
    def get_path(cls) -> Path:
        """Get the path to the LICENSE file.

        Returns:
            Path: Path to LICENSE in the project root (e.g., Path("LICENSE")).
        """
        return Path(cls.get_filename())

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the parent directory for LICENSE.

        Returns:
            Path: Empty Path() representing the project root directory.
        """
        return Path()

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the file extension for LICENSE.

        Returns:
            str: Empty string (LICENSE has no file extension).
        """
        return ""

    @classmethod
    def get_content_str(cls) -> str:
        """Get the initial LICENSE file content.

        Generates MIT license text with the current year and repository owner.

        Returns:
            str: MIT license text with placeholders filled in.

        Note:
            This method makes an external API call to GitHub and reads from
            git configuration to get the repository owner.
        """
        return cls.get_mit_license_with_year_and_owner()

    @classmethod
    def is_correct(cls) -> bool:
        """Check if the LICENSE file is valid.

        Validates that the LICENSE file exists and contains non-whitespace content.

        Returns:
            bool: True if the file exists and is non-empty (after stripping
                whitespace), False otherwise.

        Note:
            This method reads the entire LICENSE file to check if it's non-empty.
        """
        return super().is_correct() or (
            cls.get_path().exists()
            and bool(cls.get_path().read_text(encoding="utf-8").strip())
        )

    @classmethod
    @return_resource_content_on_fetch_error(resource_name="MIT_LICENSE_TEMPLATE")
    def get_mit_license(cls) -> str:
        """Fetch the MIT license text from GitHub's SPDX license API.

        Makes an HTTP request to GitHub's license API to get the MIT license
        template with placeholders for year and owner.

        Returns:
            str: MIT license text with placeholders [year] and [fullname].

        Raises:
            requests.HTTPError: If the API request fails and no fallback is
                available.

        Note:
            The @return_resource_content_on_fetch_error decorator provides a
            fallback MIT license template from resources if the API call fails.
            The returned text contains placeholders that should be replaced:
                - [year]: Current year
                - [fullname]: Copyright holder name
        """
        url = "https://api.github.com/licenses/mit"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        mit_license: str = data["body"]
        return mit_license

    @classmethod
    def get_mit_license_with_year_and_owner(cls) -> str:
        """Get the MIT license text with year and owner filled in.

        Fetches the MIT license template and replaces placeholders with the
        current year and repository owner from git configuration.

        Returns:
            str: Complete MIT license text with year and owner filled in.

        Note:
            This method makes an external API call to GitHub and reads from
            git configuration.

        Examples:
            Returns text like::

                MIT License

                Copyright (c) 2025 username

                Permission is hereby granted, free of charge, ...
        """
        mit_license = cls.get_mit_license()
        year = datetime.now(tz=UTC).year
        owner, _ = get_repo_owner_and_name_from_git(check_repo_url=False)
        mit_license = mit_license.replace("[year]", str(year))
        return mit_license.replace("[fullname]", owner)
