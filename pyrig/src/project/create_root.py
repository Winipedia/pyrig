"""Utilities for working with Python projects."""

from pyrig.dev.configs.base.base import ConfigFile


def create_root() -> None:
    """Create the project root."""
    ConfigFile.init_config_files()
