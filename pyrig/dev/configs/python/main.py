"""Configuration for the main.py entry point.

This module provides the MainConfigFile class for creating the
main.py file in the package's src directory. This file serves
as the CLI entry point.
"""

from pathlib import Path
from types import ModuleType

from pyrig import main
from pyrig.dev.configs.base.base import CopyModuleConfigFile


class MainConfigFile(CopyModuleConfigFile):
    """Configuration file manager for main.py.

    Creates a main.py in pkg_name/src that serves as the CLI entry point.
    Also cleans up any root-level main.py files.
    """

    def __init__(self) -> None:
        """Initialize and clean up any root-level main.py."""
        super().__init__()
        self.__class__.delete_root_main()

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module to copy.

        Returns:
            The pyrig.main module.
        """
        return main

    @classmethod
    def is_correct(cls) -> bool:
        """Check if the main.py file is valid.

        Allows modifications as long as the file contains a main function
        and the standard __name__ == '__main__' guard.

        Returns:
            True if the file has required structure.
        """
        return super().is_correct() or (
            "def main" in cls.get_file_content()
            and 'if __name__ == "__main__":' in cls.get_file_content()
        )

    @classmethod
    def delete_root_main(cls) -> None:
        """Delete any root-level main.py file.

        Cleans up legacy main.py files that should be in src/.
        """
        root_main_path = Path("main.py")
        if root_main_path.exists():
            root_main_path.unlink()
