"""Configuration for the {package_name}/src/main.py CLI entry point.

This module provides the MainConfigFile class for creating the
{package_name}/src/main.py file that serves as the CLI entry point for
the project.

The generated file:
    - Copies the entire pyrig.main module as a template
    - Provides a main() function as the CLI entry point
    - Includes the standard if __name__ == "__main__": guard
    - Is referenced in pyproject.toml as the CLI script entry point
    - Automatically cleans up any legacy root-level main.py files

The main.py file integrates with Click for CLI functionality and serves
as the primary interface for command-line interactions.

See Also:
    pyrig.main
        Source module that is copied as a template
    pyrig.dev.configs.pyproject.PyprojectConfigFile
        Configures the CLI script entry point
    Click documentation: https://click.palletsprojects.com/
"""

import logging
from pathlib import Path
from types import ModuleType

from pyrig import main
from pyrig.dev.configs.base.copy_module import CopyModuleConfigFile

logger = logging.getLogger(__name__)


class MainConfigFile(CopyModuleConfigFile):
    """Configuration file manager for {package_name}/src/main.py.

    Generates a {package_name}/src/main.py file by copying pyrig's main module
    as a template. This file serves as the CLI entry point for the project.

    The generated file:
        - Contains a main() function as the CLI entry point
        - Uses Click for command-line interface functionality
        - Includes the standard if __name__ == "__main__": guard
        - Is referenced in pyproject.toml [project.scripts] section
        - Can be customized with project-specific CLI commands

    Cleanup Behavior:
        - Automatically deletes any root-level main.py files on initialization
        - This ensures main.py is always in the correct location (src/)

    Examples:
        Generate {package_name}/src/main.py::

            from pyrig.dev.configs.python.main import MainConfigFile

            # Creates {package_name}/src/main.py and cleans up root main.py
            MainConfigFile()

        The generated file structure::

            \"\"\"CLI entry point for {package_name}.\"\"\"

            import click

            @click.command()
            def main():
                \"\"\"Main CLI entry point.\"\"\"
                click.echo("Hello from {package_name}!")

            if __name__ == "__main__":
                main()

    See Also:
        pyrig.main
            Source module copied as a template
        pyrig.dev.configs.pyproject.PyprojectConfigFile
            Configures the CLI script entry point
        pyrig.dev.configs.base.copy_module.CopyModuleConfigFile
            Base class for copying entire modules
    """

    def __init__(self) -> None:
        """Initialize the MainConfigFile and clean up legacy files.

        Creates the {package_name}/src/main.py file and automatically deletes
        any root-level main.py files to ensure the entry point is in the
        correct location.

        Side Effects:
            - Creates {package_name}/src/main.py
            - Deletes ./main.py if it exists (legacy cleanup)
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
        instead of in the src/ directory. This ensures the CLI entry point is
        always in the correct location.

        Side Effects:
            - Deletes ./main.py if it exists
            - Logs an info message when deletion occurs

        Note:
            This is called automatically during __init__() to ensure cleanup
            happens whenever the config file is created or updated.

        Examples:
            >>> MainConfigFile.delete_root_main()
            # Deletes ./main.py if it exists
        """
        root_main_path = Path("main.py")
        if root_main_path.exists():
            logger.info("Deleting root-level main.py file")
            root_main_path.unlink()
