r"""Plain text file configuration management.

Provides StringConfigFile for managing text files with required content and user
extensions. Validates via substring matching, preserves user additions.

Example:
    >>> from pathlib import Path
    >>> from pyrig.rig.configs.base.string_ import StringConfigFile
    >>>
    >>> class LicenseFile(StringConfigFile):
    ...     @classmethod
    ...     def parent_path(cls) -> Path:
    ...         return Path()
    ...
    ...     @classmethod
    ...     def lines(cls) -> list[str]:
    ...         return ["MIT License", "", "Copyright (c) 2024"]
    ...
    ...     @classmethod
    ...     def filename(cls) -> str:
    ...         return "LICENSE"
    ...
    ...     @classmethod
    ...     def extension(cls) -> str:
    ...         return ""
"""

from abc import abstractmethod
from typing import Any

from pyrig.rig.configs.base.list_cf import ListConfigFile


class StringConfigFile(ListConfigFile):
    r"""Abstract base class for text files with required content validation.

    Validates via substring matching, preserves user additions when updating.

    Subclasses must implement:
        - `parent_path`: Directory containing the text file
        - `lines`: Required content as list of lines
        - `extension`: File extension (can be empty string)

    See Also:
        pyrig.rig.configs.base.python.PythonConfigFile: For .py files
        pyrig.rig.configs.base.markdown.MarkdownConfigFile: For .md files
    """

    @classmethod
    @abstractmethod
    def lines(cls) -> list[str]:
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
        return cls.path().read_text(encoding="utf-8").splitlines()

    @classmethod
    def _dump(cls, config: list[str]) -> None:
        r"""Write content to file.

        Args:
            config: List of lines to write to the file.

        Note:
            User additions are preserved via merge_configs(), not here.
        """
        # add empty line at end if not already empty
        if config and config[-1].strip():
            config.append("")
        string = cls.make_string_from_lines(config)
        cls.path().write_text(string, encoding="utf-8")

    @classmethod
    def merge_configs(cls) -> list[Any]:
        """Merge expected config lines with existing file content.

        Places expected lines first, followed by existing content. If
        should_override_content() is True, existing content is discarded.

        Returns:
            Merged list of lines (expected lines first, then existing lines).
        """
        expected_lines = cls.configs()
        if not cls.should_override_content() and (actual_lines := cls.load()):
            expected_lines = [*expected_lines, *actual_lines]
        return expected_lines

    @classmethod
    def should_override_content(cls) -> bool:
        """Override file content even if it exists.

        If True the content of the StringConfigFile subclass will replace the
        existing content. If False the content will be appended to the existing
        content.

        Returns:
            True if content should be overridden, False if not.
        """
        return False

    @classmethod
    def _configs(cls) -> list[str]:
        r"""Return required content as list of lines.

        Returns:
            List of lines from lines().
        """
        return cls.lines()

    @classmethod
    def is_correct(cls) -> bool:
        r"""Check if file contains required content via substring matching.

        Returns:
            True if empty, exact match, or required content present anywhere.
        """
        all_lines_in_file = all(line in cls.file_content() for line in cls.lines())
        return super().is_correct() or all_lines_in_file

    @classmethod
    def file_content(cls) -> str:
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

                content = MyStringConfigFile.file_content()
                # Returns: "Line 1\nLine 2"
        """
        return cls.make_string_from_lines(cls.load())

    @classmethod
    def make_string_from_lines(cls, lines: list[str]) -> str:
        """Join lines with newline."""
        return "\n".join(lines)
