r"""Text-format configuration file management with content-based validation.

Defines the base class for text files that require specific content to be
present, validated via substring matching, while preserving any user additions
when the file is updated.

Example:
    >>> from pathlib import Path
    >>> from pyrig.rig.configs.base.string_ import StringConfigFile
    >>>
    >>> class LicenseFile(StringConfigFile):
    ...
    ...     def parent_path(self) -> Path:
    ...         return Path()
    ...
    ...
    ...     def lines(self) -> list[str]:
    ...         return ["MIT License", "", "Copyright (c) 2024"]
    ...
    ...
    ...     def stem(self) -> str:
    ...         return "LICENSE"
    ...
    ...
    ...     def extension(self) -> str:
    ...         return ""
"""

from abc import abstractmethod
from collections.abc import Iterable

from pyrig.core.strings import read_text_utf8, write_text_utf8
from pyrig.rig.configs.base.config_file import ConfigList, ListConfigFile


class StringConfigFile(ListConfigFile):
    r"""Abstract base class for text files with required content validation.

    Manages text configuration files by validating that required lines are
    present via substring matching, while preserving any content the user
    has added beyond what is required.

    Subclasses must implement:
        - `parent_path`: Directory containing the text file.
        - `lines`: Required content as a list of lines.
        - `extension`: File extension (can be an empty string).
    """

    @abstractmethod
    def lines(self) -> list[str]:
        r"""Return the required content that must be present in the file.

        Returns:
            List of lines checked via substring matching during validation.
        """

    def should_override_content(self) -> bool:
        """Return whether existing file content should be replaced entirely.

        Controls the merging strategy in `merge_configs`. When ``False``
        (the default), existing content is appended after the required lines,
        preserving any user additions. When ``True``, only the required lines
        are written and all existing content is discarded.

        Returns:
            ``False`` by default; override to return ``True`` when full
            replacement is desired.
        """
        return False

    def _configs(self) -> list[str]:
        r"""Return the required content as a list of lines.

        Returns:
            Lines from `lines()`.
        """
        return self.lines()

    def _load(self) -> list[str]:
        r"""Load file content as UTF-8 text and split into lines.

        Returns:
            Lines read from the file.
        """
        return self.split_lines(read_text_utf8(self.path()))

    def _dump(self, config: list[str]) -> None:
        r"""Write a list of lines to the file as UTF-8 text.

        Args:
            config: Lines to write to the file.
        """
        write_text_utf8(self.path(), self.join_lines(config))

    def merge_configs(self) -> ConfigList:
        """Merge required lines with existing file content.

        Places the required lines first, followed by the current file content.
        If `should_override_content()` returns ``True``, the existing content
        is discarded and only the required lines are kept.

        Returns:
            Merged list of lines with required content first.
        """
        expected_lines = self.configs()
        if not self.should_override_content() and (actual_lines := self.load()):
            expected_lines = [*expected_lines, *actual_lines]
        return expected_lines

    def is_correct(self) -> bool:
        r"""Check whether the file contains all required content.

        Extends the parent validation by also accepting files where every
        required line is present anywhere in the file content via substring
        matching, rather than requiring an exact structural match.

        Returns:
            ``True`` if the parent validation passes or all required lines
            are found within the file content via substring matching.
        """
        return super().is_correct() or self.all_lines_in_content(
            lines=self.configs(), content=self.file_content()
        )

    def all_lines_in_content(self, lines: Iterable[str], content: str) -> bool:
        """Check whether every line is present in the content string.

        Uses substring matching: a line is considered present if it appears
        anywhere within ``content``, not necessarily as a standalone line.

        Args:
            lines: Lines to search for.
            content: Full text to search within.

        Returns:
            ``True`` if every line in ``lines`` is a substring of ``content``.
        """
        return all(line in content for line in lines)

    def file_content(self) -> str:
        r"""Return the current file content as a single joined string."""
        return self.join_lines(self.load())

    def join_lines(self, lines: Iterable[str]) -> str:
        """Join lines with a newline character."""
        return "\n".join(lines)

    def split_lines(self, text: str) -> list[str]:
        """Split text into lines, preserving a trailing newline as an empty string.

        Unlike ``str.splitlines()``, a trailing newline in ``text`` results in
        an empty string at the end of the returned list. This ensures that
        ``join_lines(split_lines(text)) == text`` for any text ending with a
        newline.

        Args:
            text: Text to split.

        Returns:
            List of lines. If ``text`` ends with a newline, the last element
            is an empty string.
        """
        lines = text.splitlines()
        if text.endswith("\n"):
            # to preserve the lineending for join_lines
            # we add an empty string if the text ends with a newline
            lines.append("")
        return lines
