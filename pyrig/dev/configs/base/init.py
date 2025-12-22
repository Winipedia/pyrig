"""Configuration management for __init__.py files.

This module provides the InitConfigFile class for creating and
managing __init__.py files by copying the docstring from a source module.
"""

from pathlib import Path

from pyrig.dev.configs.base.copy_module_docstr import (
    CopyModuleOnlyDocstringConfigFile,
)
from pyrig.src.modules.module import get_isolated_obj_name


class InitConfigFile(CopyModuleOnlyDocstringConfigFile):
    """Config file for creating __init__.py files.

    Copies only the docstring from the source module's __init__.py.
    """

    @classmethod
    def get_filename(cls) -> str:
        """Get the __init__ filename.

        Returns:
            The string "__init__".
        """
        return "__init__"

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the directory where __init__.py will be created.

        Returns:
            Path to the package directory.
        """
        path = super().get_parent_path()
        # this path will be parent of the init file
        return path / get_isolated_obj_name(cls.get_src_module())
