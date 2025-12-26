"""Configuration for the .experiment.py scratch file.

This module provides the DotExperimentConfigFile class for creating a
.experiment.py file at the project root for local experimentation and testing.

The .experiment.py file is:
    - Automatically added to .gitignore (never committed)
    - Located at the project root for easy access
    - A safe place to test code without affecting the project
    - Useful for quick prototyping and debugging

This allows developers to experiment with code locally without cluttering
version control or affecting the project structure.

See Also:
    pyrig.dev.configs.git.gitignore.GitIgnoreConfigFile
        Automatically adds .experiment to .gitignore
"""

from pathlib import Path

from pyrig.dev.configs.base.python import PythonConfigFile


class DotExperimentConfigFile(PythonConfigFile):
    """Configuration file manager for .experiment.py.

    Generates a .experiment.py scratch file at the project root for local
    experimentation. The file is automatically excluded from version control
    via .gitignore, making it safe for testing and prototyping.

    Use Cases:
        - Quick code prototyping
        - Testing new features locally
        - Debugging without modifying project files
        - Experimenting with APIs and libraries

    The file is minimal by design, containing only a docstring. Developers
    can add any code they want without worrying about committing it.

    Examples:
        Generate .experiment.py::

            from pyrig.dev.configs.python.dot_experiment import DotExperimentConfigFile

            # Creates .experiment.py in project root
            DotExperimentConfigFile()

        Use for experimentation::

            # In .experiment.py
            from myproject import some_module

            # Test code here - won't be committed
            result = some_module.test_function()
            print(result)

    Note:
        This file is automatically added to .gitignore by GitIgnoreConfigFile.

    See Also:
        pyrig.dev.configs.git.gitignore.GitIgnoreConfigFile
            Adds .experiment to .gitignore patterns
    """

    @classmethod
    def get_filename(cls) -> str:
        """Get the experiment filename.

        Returns:
            str: The string ".experiment" (extension .py is added by parent class).
        """
        return ".experiment"

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the parent directory for .experiment.py.

        Returns:
            Path: Empty Path() representing the project root directory.
        """
        return Path()

    @classmethod
    def get_content_str(cls) -> str:
        '''Get the .experiment.py file content.

        Generates minimal Python file content with just a docstring explaining
        the file's purpose.

        Returns:
            str: Python file content with a docstring.

        Examples:
            Returns::

                """This file is for experimentation and is ignored by git."""
        '''
        return '''"""This file is for experimentation and is ignored by git."""
'''
