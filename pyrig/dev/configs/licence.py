"""Config utilities for LICENSE."""

from pathlib import Path

from pyrig.dev.configs.base.base import TextConfigFile


class LicenceConfigFile(TextConfigFile):
    """Config file for LICENSE."""

    @classmethod
    def get_filename(cls) -> str:
        """Get the filename of the config file."""
        return "LICENSE"

    @classmethod
    def get_path(cls) -> Path:
        """Get the path to the config file."""
        return Path(cls.get_filename())

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the path to the config file."""
        return Path()

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the file extension of the config file."""
        return ""

    @classmethod
    def get_content_str(cls) -> str:
        """Get the content."""
        return ""
