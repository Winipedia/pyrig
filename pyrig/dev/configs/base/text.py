r"""Plain text file configuration management.

Provides TextConfigFile for managing text files with required content and user
extensions. Validates via substring matching, preserves user additions.

Example:
    >>> from pathlib import Path
    >>> from pyrig.dev.configs.base.text import TextConfigFile
    >>>
    >>> class LicenseFile(TextConfigFile):
    ...     @classmethod
    ...     def get_parent_path(cls) -> Path:
    ...         return Path()
    ...
    ...     @classmethod
    ...     def get_content_str(cls) -> str:
    ...         return "MIT License\n\nCopyright (c) 2024"
    ...
    ...     @classmethod
    ...     def get_filename(cls) -> str:
    ...         return "LICENSE"
    ...
    ...     @classmethod
    ...     def get_file_extension(cls) -> str:
    ...         return ""
"""

from abc import abstractmethod
from typing import Any

from pyrig.dev.configs.base.base import ConfigFile


class TextConfigFile(ConfigFile):
    r"""Abstract base class for text files with required content validation.

    Validates via substring matching, preserves user additions when updating.

    Attributes:
        CONTENT_KEY: Dictionary key for file content ("content").

    Subclasses must implement:
        - `get_parent_path`: Directory containing the text file
        - `get_content_str`: Required content that must be present
        - `get_file_extension`: File extension (can be empty string)

    See Also:
        pyrig.dev.configs.base.python.PythonConfigFile: For .py files
        pyrig.dev.configs.base.markdown.MarkdownConfigFile: For .md files
    """

    CONTENT_KEY = "content"

    @classmethod
    @abstractmethod
    def get_content_str(cls) -> str:
        r"""Return required content that must be present in file.

        Returns:
            Content string validated via substring matching.
        """

    @classmethod
    def load(cls) -> dict[str, str]:
        r"""Load file content as UTF-8 text wrapped in dict.

        Returns:
            Dict with CONTENT_KEY containing full file content.
        """
        return {cls.CONTENT_KEY: cls.get_path().read_text(encoding="utf-8")}

    @classmethod
    def dump(cls, config: dict[str, Any] | list[Any]) -> None:
        r"""Write content to file, preserving user additions by appending.

        Args:
            config: Dict with content under CONTENT_KEY.

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
        r"""Return dict with required content under CONTENT_KEY.

        Returns:
            Dict with required content from get_content_str().
        """
        return {cls.CONTENT_KEY: cls.get_content_str()}

    @classmethod
    def is_correct(cls) -> bool:
        r"""Check if file contains required content via substring matching.

        Returns:
            True if empty, exact match, or required content present anywhere.
        """
        return (
            super().is_correct()
            or cls.get_content_str().strip() in cls.get_file_content()
        )

    @classmethod
    def get_file_content(cls) -> str:
        r"""Get the current file content.

        Convenience method to get the file content as a string without the
        dict wrapper. Equivalent to cls.load()[cls.CONTENT_KEY].

        Returns:
            The full content of the file as a string.

        Example:
            Get file content::

                # myfile.txt contains:
                # Line 1
                # Line 2

                content = MyTextConfigFile.get_file_content()
                # Returns: "Line 1\nLine 2\n"
        """
        return cls.load()[cls.CONTENT_KEY]
