"""Text-format configuration file management with content-based validation."""

from abc import abstractmethod
from collections.abc import Iterable

from pyrig.core.strings import read_text_utf8, write_text_utf8
from pyrig.rig.configs.base.config_file import ListConfigFile


class StringConfigFile(ListConfigFile):
    """Abstract base class for text files with required content validation.

    Manages text configuration files by validating that required lines are
    present as exact list items, while preserving any content the user has
    added beyond what is required.
    """

    @abstractmethod
    def content(self) -> str:
        """Return the text that must be present in the file.

        Returns:
            Required text. Each line is checked independently for
            presence anywhere in the file; lines need not be
            contiguous, ordered, or exact matches.
        """

    def lines(self) -> list[str]:
        """Return the required content split into individual lines.

        Returns:
            The result of splitting `content()` into lines.
        """
        return self.split_lines(self.content())

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

    def read_content(self) -> str:
        """Return the current file content as a single joined string."""
        return self.join_lines(self.safe_load())

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
