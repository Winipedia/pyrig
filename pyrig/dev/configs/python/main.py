"""Config utilities for main.py."""

from pathlib import Path
from types import ModuleType

from pyrig import main
from pyrig.dev.configs.base.base import CopyModuleConfigFile


class MainConfigFile(CopyModuleConfigFile):
    """Config file for main.py.

    Creates a main.py in pkg_name/src.
    """

    def __init__(self) -> None:
        """Initialize the config file."""
        super().__init__()
        self.__class__.delete_root_main()

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module."""
        return main

    @classmethod
    def is_correct(cls) -> bool:
        """Check if the config is correct.

        Allow modifications to the main func and __name__ == '__main__' line.
        """
        return super().is_correct() or (
            "def main" in cls.get_file_content()
            and 'if __name__ == "__main__":' in cls.get_file_content()
        )

    @classmethod
    def delete_root_main(cls) -> None:
        """Delete the root main.py."""
        root_main_path = Path("main.py")
        if root_main_path.exists():
            root_main_path.unlink()
