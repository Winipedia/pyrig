"""Configuration for .experiment.py scratch file.

Generates .experiment.py at project root for local experimentation. Automatically
added to .gitignore (never committed).

See Also:
    pyrig.dev.configs.git.gitignore.GitIgnoreConfigFile
"""

from pathlib import Path

from pyrig.dev.configs.base.python import PythonConfigFile


class DotExperimentConfigFile(PythonConfigFile):
    """Manages .experiment.py scratch file.

    Generates .experiment.py at project root for local experimentation. Automatically
    excluded from version control via .gitignore.

    Examples:
        Generate .experiment.py::

            DotExperimentConfigFile()

        Use for experimentation::

            # In .experiment.py
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
        """Get the experiment filename.

        Returns:
            str: ".experiment" (extension .py added by parent class).
        """
        return ".experiment"

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the parent directory for .experiment.py.

        Returns:
            Path: Empty Path() (project root).
        """
        return Path()

    @classmethod
    def get_lines(cls) -> list[str]:
        """Get the .experiment.py file content.

        Returns:
            List of lines with Python docstring.
        """
        return ['"""This file is for experimentation and is ignored by git."""', ""]

    @classmethod
    def is_correct(cls) -> bool:
        """Check if the .experiment.py file is valid.

        Returns:
            True if the file exists.
        """
        return super().is_correct() or (cls.get_path().exists())
