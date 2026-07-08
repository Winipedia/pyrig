"""Text-format configuration file management with content-based validation."""

from abc import abstractmethod
from collections.abc import Iterable
from typing import Any

from pyrig.core.strings import read_text_utf8, write_text_utf8
from pyrig.rig.configs.base.config_file import ListConfigFile


class StringConfigFile(ListConfigFile):
    """Abstract base class for text files with required content validation.

    Manages text configuration files by validating that required lines are
    present via substring matching, while preserving any content the user
    has added beyond what is required.
    """

    @abstractmethod
    def lines(self) -> list[str]:
        """Return the lines that must be present in the file.

        Returns:
            Required lines, checked via substring matching rather than
            exact line equality.
        """

    def _configs(self) -> list[str]:
        """Return the required lines."""
        return self.lines()

    def _dump(self, configs: list[str]) -> None:
        """Join the lines and write them to the file as UTF-8 text.

        Args:
            configs: Lines to write to the file.
        """
        write_text_utf8(self.path(), self.join_lines(configs))

    def _load(self) -> list[str]:
        """Read the file as UTF-8 text and split it into lines."""
        return self.split_lines(read_text_utf8(self.path()))

    def is_correct(self) -> bool:
        """Check whether the file already contains all required content.

        A required line need not be an exact line of the file; it only has
        to occur somewhere within the file's text.

        Returns:
            `True` if every required line is present in the file.
        """
        return self.all_lines_in_content(
            lines=self.configs(), content=self.read_content()
        )

    def merge_configs(self) -> list[Any]:
        """Merge required lines with existing file content.

        Places the required lines first, followed by the current file content.
        If `should_override_content()` returns `True`, the existing content
        is discarded and only the required lines are returned.

        Returns:
            The lines for the updated file, with required content first.
        """
        expected_lines = self.configs()
        if self.should_override_content():
            return expected_lines
        return [*expected_lines, *self.load()]

    def should_override_content(self) -> bool:
        """Return whether existing file content should be discarded.

        Defaults to `False`. Override in subclasses that must replace the
        file's content instead of preserving it.

        Returns:
            `True` if existing content should be discarded; `False` otherwise.
        """
        return False

    def all_lines_in_content(self, lines: Iterable[str], content: str) -> bool:
        """Check whether every line is present in the content string.

        Uses substring matching: a line is considered present if it appears
        anywhere within `content`, not necessarily as a standalone line.

        Args:
            lines: Lines to search for.
            content: Full text to search within.

        Returns:
            `True` if every line in `lines` is a substring of `content`.
        """
        return all(line in content for line in lines)

    def read_content(self) -> str:
        """Return the current file content as a single joined string."""
        return self.join_lines(self.load())

    def write_content(self, content: str) -> None:
        """Write the given content string to the file, replacing existing content."""
        self.dump(self.split_lines(content))

    def join_lines(self, lines: Iterable[str]) -> str:
        """Join lines with a newline character."""
        return "\n".join(lines)

    def split_lines(self, text: str) -> list[str]:
        """Split text into lines, preserving a trailing newline as an empty string.

        Unlike `str.splitlines()`, a trailing newline in `text` results in
        an empty string at the end of the returned list. This ensures that
        `join_lines(split_lines(text)) == text` for any text ending with a
        newline.

        Args:
            text: Text to split.

        Returns:
            List of lines. If `text` ends with a newline, the last element
            is an empty string.
        """
        lines = text.splitlines()
        if text.endswith("\n"):
            lines.append("")
        return lines
