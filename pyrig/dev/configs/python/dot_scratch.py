"""Configuration for .scratch.py scratch file.

Generates .scratch.py at project root for local experimentation. Automatically
added to .gitignore (never committed).

See Also:
    pyrig.dev.configs.git.gitignore.GitIgnoreConfigFile
"""

from pathlib import Path

from pyrig.dev.configs.base.python import PythonConfigFile


class DotScratchConfigFile(PythonConfigFile):
    """Manages .scratch.py scratch file.

    Generates .scratch.py at project root for local experimentation. Automatically
    excluded from version control via .gitignore.

    Examples:
        Generate .scratch.py::

            DotScratchConfigFile()

        Use for experimentation::

            # In .scratch.py
            from myproject import some_module

            # Test code here - won't be committed
            result = some_module.test_function()
            print(result)

    Note:
        Automatically added to .gitignore by GitIgnoreConfigFile.

    See Also:
        pyrig.dev.configs.git.gitignore.GitIgnoreConfigFile
    """

    @classmethod
    def get_filename(cls) -> str:
        """Get the scratch filename.

        Returns:
            str: ".scratch" (extension .py added by parent class).
        """
        return ".scratch"

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the parent directory for .scratch.py.

        Returns:
            Path: Empty Path() (project root).
        """
        return Path()

    @classmethod
    def get_lines(cls) -> list[str]:
        """Get the .scratch.py file content.

        Returns:
            List of lines with Python docstring.
        """
        return ['"""This file is for scratch work and is ignored by git."""']

    @classmethod
    def is_correct(cls) -> bool:
        """Check if the .scratch.py file is valid.

        Returns:
            True if the file exists.
        """
        return cls.get_path().exists()
