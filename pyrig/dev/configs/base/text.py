"""Configuration management for plain text files.

This module provides the TextConfigFile class
for managing plain text configuration files.
"""

from abc import abstractmethod
from typing import Any

from pyrig.dev.configs.base.base import ConfigFile


class TextConfigFile(ConfigFile):
    """Abstract base class for plain text configuration files.

    Suitable for files that have a required starting content but can
    be extended by the user (e.g., Python files, README.md).

    Attributes:
        CONTENT_KEY: Dictionary key used to store file content.
    """

    CONTENT_KEY = "content"

    @classmethod
    @abstractmethod
    def get_content_str(cls) -> str:
        """Get the required content for this file.

        Returns:
            The content string that must be present in the file.
        """

    @classmethod
    def load(cls) -> dict[str, str]:
        """Load the text file content.

        Returns:
            Dict with the file content under CONTENT_KEY.
        """
        return {cls.CONTENT_KEY: cls.get_path().read_text(encoding="utf-8")}

    @classmethod
    def dump(cls, config: dict[str, Any] | list[Any]) -> None:
        """Write content to the text file.

        Appends existing file content to preserve user additions.

        Args:
            config: Dict containing the content to write.

        Raises:
            TypeError: If config is not a dict.
        """
        if not isinstance(config, dict):
            msg = f"Cannot dump {config} to text file."
            raise TypeError(msg)
        if cls.get_file_content().strip():
            config[cls.CONTENT_KEY] = (
                config[cls.CONTENT_KEY] + "\n" + cls.get_file_content()
            )
        cls.get_path().write_text(config[cls.CONTENT_KEY], encoding="utf-8")

    @classmethod
    def get_configs(cls) -> dict[str, Any]:
        """Get the expected configuration structure.

        Returns:
            Dict with the required content under CONTENT_KEY.
        """
        return {cls.CONTENT_KEY: cls.get_content_str()}

    @classmethod
    def is_correct(cls) -> bool:
        """Check if the text file contains the required content.

        Returns:
            True if the required content is present in the file.
        """
        return (
            super().is_correct()
            or cls.get_content_str().strip() in cls.load()[cls.CONTENT_KEY]
        )

    @classmethod
    def get_file_content(cls) -> str:
        """Get the current file content.

        Returns:
            The full content of the file.
        """
        return cls.load()[cls.CONTENT_KEY]
