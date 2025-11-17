"""Configs for py_dev.

All subclasses of ConfigFile in the configs package are automatically called.
"""

from pathlib import Path

from py_dev.dev import configs
from py_dev.dev.configs.base.base import PythonPackageConfigFile
from py_dev.dev.configs.pyproject import PyprojectConfigFile
from py_dev.utils.modules.module import to_path


class ConfigsConfigFile(PythonPackageConfigFile):
    """Config file for configs.py."""

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the path to the config file."""
        src_package = PyprojectConfigFile.get_package_name()
        builds_package = cls.get_module_name_replacing_start_module(
            configs, src_package
        )
        return to_path(builds_package, is_package=True)

    @classmethod
    def get_content_str(cls) -> str:
        """Get the content."""
        return '''"""Configs for py_dev.

All subclasses of ConfigFile in the configs package are automatically called.
"""
'''
