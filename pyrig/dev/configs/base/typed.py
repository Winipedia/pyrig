"""Configuration management for py.typed marker files.

This module provides the TypedConfigFile class for managing py.typed files.
"""

from typing import Any

from pyrig.dev.configs.base.base import ConfigFile


class TypedConfigFile(ConfigFile):
    """Config file for py.typed marker files.

    Creates empty py.typed files to indicate PEP 561 compliance.
    """

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the typed file extension.

        Returns:
            The string "typed".
        """
        return "typed"

    @classmethod
    def load(cls) -> dict[str, Any] | list[Any]:
        """Load the py.typed file (always empty).

        Returns:
            An empty dict.
        """
        return {}

    @classmethod
    def dump(cls, config: dict[str, Any] | list[Any]) -> None:
        """Validate that py.typed files remain empty.

        Args:
            config: Must be empty.

        Raises:
            ValueError: If config is not empty.
        """
        if config:
            msg = "Cannot dump to py.typed file."
            raise ValueError(msg)

    @classmethod
    def get_configs(cls) -> dict[str, Any] | list[Any]:
        """Get the expected configuration (empty).

        Returns:
            An empty dict.
        """
        return {}
