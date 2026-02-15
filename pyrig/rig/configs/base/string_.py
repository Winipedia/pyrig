r"""String-based configuration file management.

Provides StringConfigFile for managing text-format config files with required
content. Validates via substring matching, preserves user additions.

Example:
    >>> from pathlib import Path
    >>> from pyrig.rig.configs.base.string_ import StringConfigFile
    >>>
    >>> class LicenseFile(StringConfigFile):
    ...
    ...     def parent_path(self) -> Path:
    ...     def parent_path(self) -> Path:
    ...
    ...
    ...     def lines(self) -> list[str]:
    ...     def lines(self) -> list[str]:
    ...
    ...
    ...     def filename(self) -> str:
    ...     def filename(self) -> str:
    ...
    ...
    ...     def extension(self) -> str:
    ...     def extension(self) -> str:
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

    @abstractmethod
    def lines(self) -> list[str]:
        r"""Return required content that must be present in file.

        Returns:
            List of lines validated via substring matching.
    def lines(self) -> list[str]:

    def _load(self) -> list[str]:
        r"""Load file content as UTF-8 text.

        Returns:
            List of lines from the file.
        """
        return self.path().read_text(encoding="utf-8").splitlines()

    def _dump(self, config: list[str]) -> None:
        r"""Write content to file.

        Args:
            config: List of lines to write to the file.

        Note:
            User additions are preserved via `merge_configs()`, not here.
        """
        # add empty line at end if not already empty
        if config and config[-1].strip():
            config.append("")
        string = self.make_string_from_lines(config)
        self.path().write_text(string, encoding="utf-8")

    def merge_configs(self) -> list[Any]:
        """Merge expected config lines with existing file content.

        Place expected lines first, followed by existing content. If
        `should_override_content()` is ``True``, existing content is discarded.

        Returns:
            Merged list of lines (expected lines first, then existing lines).
        """
        expected_lines = self.configs()
        if not self.should_override_content() and (actual_lines := self.load()):
            expected_lines = [*expected_lines, *actual_lines]
        return expected_lines

    def should_override_content(self) -> bool:
        """Return whether existing content should be replaced entirely.

        If ``True``, the expected content replaces the existing content entirely.
        If ``False``, the existing content is appended after the expected content.

        Returns:
            ``True`` if content should be overridden, ``False`` if not.
        """
        return False

    def _configs(self) -> list[str]:
        r"""Return required content as list of lines.

        Returns:
            List of lines from `lines()`.
        """
        return self.lines()

    def is_correct(self) -> bool:
        r"""Check if file contains required content via substring matching.

        Returns:
            ``True`` if parent validation passes or all required lines found
            in file content.
    def is_correct(self) -> bool:
        all_lines_in_file = all(line in self.file_content() for line in self.lines())
        return super().is_correct() or all_lines_in_file

    def file_content(self) -> str:
        r"""Return file content as a single string by joining lines from `load()`.

        Returns:
            File content as a single string with lines joined by newlines.
        """
        return self.make_string_from_lines(self.load())

    def make_string_from_lines(self, lines: list[str]) -> str:
        """Join lines with newline.

        Args:
            lines: List of strings to join.

        Returns:
            Single string with lines joined by newline characters.
        """
        return "\n".join(lines)
