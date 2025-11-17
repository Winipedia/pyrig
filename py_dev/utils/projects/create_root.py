"""Utilities for working with Python projects."""

from py_dev.dev.configs.base.base import ConfigFile
from py_dev.dev.configs.pyproject import PyprojectConfigFile
from py_dev.utils.modules.module import create_module
from py_dev.utils.testing.convention import TESTS_PACKAGE_NAME


def create_root() -> None:
    """Create the project root."""
    src_package_name = PyprojectConfigFile.get_package_name()
    create_module(src_package_name, is_package=True)
    create_module(TESTS_PACKAGE_NAME, is_package=True)
    ConfigFile.init_config_files()
