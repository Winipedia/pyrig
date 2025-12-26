"""Configuration for the {package_name}/main.py template file.

This module provides the MainConfigFile class for creating the
{package_name}/main.py file that provides an empty main() function template.

The generated file:
    - Copies the entire pyrig.main module as a template
    - Provides an empty main() function that can be customized
    - Includes the standard if __name__ == "__main__": guard
    - Gets automatically discovered and registered as a CLI command by
      pyrig.dev.cli.cli
    - Automatically cleans up any legacy root-level main.py files

The main() function is discovered by pyrig's CLI system and registered as a
Typer command, but the template itself contains no CLI functionality.

See Also:
    pyrig.main
        Source module that is copied as a template
    pyrig.dev.cli.cli
        CLI system that discovers and registers the main() function
    pyrig.dev.configs.pyproject.PyprojectConfigFile
        Configures the CLI script entry point (pyrig.dev.cli.cli:main)
"""

import logging
from pathlib import Path
from types import ModuleType

from pyrig import main
from pyrig.dev.configs.base.copy_module import CopyModuleConfigFile

logger = logging.getLogger(__name__)


class MainConfigFile(CopyModuleConfigFile):
    """Configuration file manager for {package_name}/main.py.

    Generates a {package_name}/main.py file by copying pyrig's main module
    as a template. This file provides an empty main() function that gets
    automatically discovered and registered as a CLI command.

    The generated file:
        - Contains an empty main() function template
        - Includes the standard if __name__ == "__main__": guard
        - Gets discovered by pyrig.dev.cli.cli.add_subcommands()
        - Gets registered as a Typer command automatically
        - Can be customized with project-specific application logic

    Cleanup Behavior:
        - Automatically deletes any root-level main.py files on initialization
        - This ensures main.py is always in the correct location ({package_name}/)

    Examples:
        Generate {package_name}/main.py::

            from pyrig.dev.configs.python.main import MainConfigFile

            # Creates {package_name}/main.py and cleans up root main.py
            MainConfigFile()

        The generated file structure::

            \"\"\"Main entrypoint for the project.\"\"\"


            def main() -> None:
                \"\"\"Main entrypoint for the project.\"\"\"


            if __name__ == "__main__":
                main()

    See Also:
        pyrig.main
            Source module copied as a template
        pyrig.dev.cli.cli.add_subcommands
            Function that discovers and registers the main() function
        pyrig.dev.configs.base.copy_module.CopyModuleConfigFile
            Base class for copying entire modules
    """

    def __init__(self) -> None:
        """Initialize the MainConfigFile and clean up legacy files.

        Creates the {package_name}/main.py file and automatically deletes
        any root-level main.py files to ensure the file is in the correct
        location.

        Side Effects:
            - Creates {package_name}/main.py
            - Deletes ./main.py if it exists (legacy cleanup from uv init)
            - Logs deletion of root-level main.py if found
        """
        super().__init__()
        self.__class__.delete_root_main()

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module to copy.

        Returns:
            ModuleType: The pyrig.main module.

        Note:
            The entire module is copied, not just the docstring. Users can
            then customize the generated file for their project.
        """
        return main

    @classmethod
    def is_correct(cls) -> bool:
        """Check if the main.py file is valid.

        Validates that the file contains the required structure: a main()
        function and the standard if __name__ == "__main__": guard. Allows
        user modifications as long as these core elements are present.

        Returns:
            bool: True if the file contains "def main" and the __main__ guard,
                False otherwise.

        Note:
            This method reads the file from disk to check its content.

        Examples:
            Valid main.py structure::

                def main():
                    \"\"\"CLI entry point.\"\"\"
                    pass

                if __name__ == "__main__":
                    main()
        """
        return super().is_correct() or (
            "def main" in cls.get_file_content()
            and 'if __name__ == "__main__":' in cls.get_file_content()
        )

    @classmethod
    def delete_root_main(cls) -> None:
        """Delete any root-level main.py file.

        Cleans up legacy main.py files that were created at the project root
        by uv init. This ensures main.py is always in the correct location
        ({package_name}/ directory).

        Side Effects:
            - Deletes ./main.py if it exists
            - Logs an info message when deletion occurs

        Note:
            This is called automatically during __init__() to ensure cleanup
            happens whenever the config file is created or updated. The uv
            init command creates a main.py at the project root, which needs
            to be removed.

        Examples:
            >>> MainConfigFile.delete_root_main()
            # Deletes ./main.py if it exists
        """
        root_main_path = Path("main.py")
        if root_main_path.exists():
            logger.info("Deleting root-level main.py file")
            root_main_path.unlink()
