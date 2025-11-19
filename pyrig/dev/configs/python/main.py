"""Config utilities for main.py."""

from types import ModuleType

from pyrig import main
from pyrig.dev.configs.base.base import CopyModuleConfigFile


class MainConfigFile(CopyModuleConfigFile):
    """Config file for main.py.

    Creates a main.py in pkg_name/src.
    """

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
