"""Config File for README.md."""

from pathlib import Path

import pyrig
from pyrig.dev.configs.base.base import TextConfigFile
from pyrig.dev.configs.pyproject import PyprojectConfigFile


class ReadmeConfigFile(TextConfigFile):
    """Config file for README.md."""

    @classmethod
    def get_filename(cls) -> str:
        """Get the filename of the config file."""
        return "README"

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the path to the config file."""
        return Path()

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the file extension of the config file."""
        return "md"

    @classmethod
    def get_content_str(cls) -> str:
        """Get the content."""
        content = f"""# {PyprojectConfigFile.get_project_name()}
"""
        if PyprojectConfigFile.get_project_name() != pyrig.__name__:
            content += f"""
(This project uses [{PyprojectConfigFile.get_project_name_from_pkg_name(pyrig.__name__)}](https://github.com/Winipedia/{pyrig.__name__}))
"""
        return content
