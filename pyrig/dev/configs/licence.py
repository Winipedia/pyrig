"""Configuration management for LICENSE files.

This module provides the LicenceConfigFile class for managing the
project's LICENSE file. The file is created empty and users are
expected to add their own license text.
"""

from pathlib import Path

from pyrig.dev.configs.base.base import TextConfigFile


class LicenceConfigFile(TextConfigFile):
    """Configuration file manager for LICENSE.

    Creates an empty LICENSE file in the project root. Users should
    add their preferred license text manually.
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
        return ""
