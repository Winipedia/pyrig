"""Configuration for the .experiment.py scratch file.

This module provides the DotExperimentConfigFile class for creating
a .experiment.py file at the project root for local experimentation.
This file is automatically added to .gitignore.
"""

from pathlib import Path

from pyrig.dev.configs.base.base import PythonConfigFile


class DotExperimentConfigFile(PythonConfigFile):
    """Configuration file manager for .experiment.py.

    Creates a scratch Python file at the project root for local
    experimentation. This file is excluded from version control.
    """

    @classmethod
    def get_filename(cls) -> str:
        """Get the experiment filename.

        Returns:
            The string ".experiment".
        """
        return ".experiment"

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the project root directory.

        Returns:
            Path to the project root.
        """
        return Path()

    @classmethod
    def get_content_str(cls) -> str:
        """Get the experiment file content.

        Returns:
            A minimal Python file with a docstring.
        """
        return '''"""This file is for experimentation and is ignored by git."""
'''
