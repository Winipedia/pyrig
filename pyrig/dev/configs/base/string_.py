r"""Plain text file configuration management.

Provides StringConfigFile for managing text files with required content and user
extensions. Validates via substring matching, preserves user additions.

Example:
    >>> from pathlib import Path
    >>> from pyrig.dev.configs.base.string_ import StringConfigFile
    >>>
    >>> class LicenseFile(StringConfigFile):
    ...     @classmethod
    ...     def get_parent_path(cls) -> Path:
    ...         return Path()
    ...
    ...     @classmethod
    ...     def get_lines(cls) -> list[str]:
    ...         return ["MIT License", "", "Copyright (c) 2024"]
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

from pyrig.dev.configs.base.list_cf import ListConfigFile


class StringConfigFile(ListConfigFile):
    r"""Abstract base class for text files with required content validation.

    Validates via substring matching, preserves user additions when updating.

    Subclasses must implement:
        - `get_parent_path`: Directory containing the text file
        - `get_lines`: Required content as list of lines
        - `get_file_extension`: File extension (can be empty string)

    See Also:
        pyrig.dev.configs.base.python.PythonConfigFile: For .py files
        pyrig.dev.configs.base.markdown.MarkdownConfigFile: For .md files
    """

    @classmethod
    @abstractmethod
    def get_lines(cls) -> list[str]:
        r"""Return required content that must be present in file.

        Returns:
            List of lines validated via substring matching.
        """

    @classmethod
    def _load(cls) -> list[str]:
        r"""Load file content as UTF-8 text.

        Returns:
            List of lines from the file.
        """
        return cls.get_path().read_text(encoding="utf-8").splitlines()

    @classmethod
    def _dump(cls, config: list[str]) -> None:
        r"""Write content to file.

        Args:
            config: List of lines to write to the file.

        Note:
            User additions are preserved via add_missing_configs(), not here.
        """
        string = cls.make_string_from_lines(config)
        cls.get_path().write_text(string, encoding="utf-8")

    @classmethod
    def add_missing_configs(cls) -> list[Any]:
        """Merge expected config lines with existing file content.

        Places expected lines first, followed by existing content. If
        override_content() is True, existing content is discarded.

        Returns:
            Merged list of lines (expected lines first, then existing lines).
        """
        actual_lines = cls.load()
        expected_lines = cls.get_configs()
        if not cls.override_content() and actual_lines:
            expected_lines = [*expected_lines, *actual_lines]
        return expected_lines

    @classmethod
    def override_content(cls) -> bool:
        """Override file content even if it exists.

        If True the content of the StringConfigFile subclass will replace the
        existing content. If False the content will be appended to the existing
        content.

        Returns:
            True if content should be overridden, False if not.
        """
        return False

    @classmethod
    def _get_configs(cls) -> list[str]:
        r"""Return required content as list of lines.

        Returns:
            List of lines from get_lines().
        """
        return cls.get_lines()

    @classmethod
    def is_correct(cls) -> bool:
        r"""Check if file contains required content via substring matching.

        Returns:
            True if empty, exact match, or required content present anywhere.
        """
        all_lines_in_file = all(
            line in cls.get_file_content() for line in cls.get_lines()
        )
        return super().is_correct() or all_lines_in_file

    @classmethod
    def get_file_content(cls) -> str:
        r"""Get the current file content.

        Convenience method to get the file content as a string by joining
        the lines from load().

        Returns:
            The full content of the file as a string.

        Example:
            Get file content::

                # myfile.txt contains:
                # Line 1
                # Line 2

                content = MyStringConfigFile.get_file_content()
                # Returns: "Line 1\nLine 2"
        """
        return cls.make_string_from_lines(cls.load())

    @classmethod
    def make_string_from_lines(cls, lines: list[str]) -> str:
        """Join lines with newline."""
        return "\n".join(lines)
