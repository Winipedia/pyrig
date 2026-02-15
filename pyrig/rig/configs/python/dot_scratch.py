"""Configuration for .scratch.py scratch file.

Generates .scratch.py at project root for local experimentation. Automatically
added to .gitignore (never committed).

See Also:
    pyrig.rig.configs.git.gitignore.GitignoreConfigFile
"""

from pathlib import Path

from pyrig.rig.configs.base.python import PythonConfigFile


class DotScratchConfigFile(PythonConfigFile):
    """Manages .scratch.py scratch file.

    Generates .scratch.py at project root for local experimentation. Automatically
    excluded from version control via .gitignore.

    Examples:
        Generate .scratch.py::

            DotScratchConfigFile.I.validate()

    Note:
        Automatically added to .gitignore by GitignoreConfigFile.I.

    See Also:
        pyrig.rig.configs.git.gitignore.GitignoreConfigFile
    """

    def filename(self) -> str:
        """Get the scratch filename.

        Returns:
            str: ".scratch" (extension .py added by parent class).
        """
        return ".scratch"

    def parent_path(self) -> Path:
        """Get the parent directory for .scratch.py.

        Returns:
            Path: Empty Path() (project root).
        """
        return Path()

    def lines(self) -> list[str]:
        """Get the .scratch.py file content.

        Returns:
            list[str]: Content lines for the scratch file.
        """
        return ['"""This file is for scratch work and is ignored by git."""']

    def is_correct(self) -> bool:
        """Check if the .scratch.py file is valid.

        Returns:
            bool: True if the file exists.
        """
        return self.path().exists()
