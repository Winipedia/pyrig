"""Config utilities for subcommands.py."""

from pathlib import Path

from pyrig.dev import cli
from pyrig.dev.configs.base.base import PythonPackageConfigFile
from pyrig.dev.configs.pyproject import PyprojectConfigFile
from pyrig.utils.modules.module import to_path


class SubcommandsConfigFile(PythonPackageConfigFile):
    """Config file for subcommands.py."""

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the path to the config file."""
        src_package = PyprojectConfigFile.get_package_name()
        builds_package = cls.get_module_name_replacing_start_module(cli, src_package)
        return to_path(builds_package, is_package=True)

    @classmethod
    def get_content_str(cls) -> str:
        """Get the config."""
        return '''"""Subcommands for the CLI.

They will be automatically imported and added to the CLI
IMPORTANT: All funcs in this file will be added as subcommands.
So best to define the logic elsewhere and just call it here in a wrapper.
"""
'''
