"""Utilities for working with strings and text files."""

import re
from collections.abc import Iterator
from pathlib import Path
from typing import IO, Any

UTF_8_ENCODING = "utf-8"


def open_path_with_utf8(path: Path, *, mode: str = "r") -> IO[Any]:
    r"""Open a file with UTF-8 encoding and no newline translation.

    Uses `newline="\n"`, so line endings are read and written exactly as
    they appear instead of being translated to or from the platform's line
    separator (`\r\n` on Windows).

    Args:
        path: Path to the file to open.
        mode: Mode in which to open the file (default is `"r"` for reading).

    Returns:
        The opened file object.
    """
    return path.open(mode=mode, encoding=UTF_8_ENCODING, newline="\n")


def read_text_utf8(path: Path) -> str:
    """Read the text content of a file using UTF-8 encoding.

    Returns:
        The file's content as a UTF-8-decoded string.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    return path.read_text(encoding=UTF_8_ENCODING)


def write_text_utf8(path: Path, content: str) -> int:
    r"""Write `content` to `path` as UTF-8, replacing any existing file.

    Uses `newline="\n"` so `\n` characters in `content` are written as-is
    instead of being translated to the platform's line separator (`\r\n`
    on Windows), keeping output consistent across platforms.

    Returns:
        The number of characters written.
    """
    return path.write_text(content, encoding=UTF_8_ENCODING, newline="\n")


def is_multiline(string: str) -> bool:
    """Check whether a string contains one or more newline characters."""
    return "\n" in string


def make_linked_badge_markdown(
    image_url: str,
    link_url: str,
    alt_text: str,
) -> str:
    """Return Markdown for a clickable badge image.

    Args:
        image_url: URL of the image.
        link_url: URL the image should link to when clicked.
        alt_text: Alternative text for the image (used for accessibility).

    Returns:
        Markdown string in the form `[![alt_text](image_url)](link_url)`.
    """
    return f"[![{alt_text}]({image_url})]({link_url})"


def reformat_name(
    name: str,
    *,
    split_on: str,
    join_on: str,
    capitalize: bool = False,
) -> str:
    """Split a name on one separator and rejoin the parts with another.

    Empty parts produced by the split are discarded.

    Args:
        name: The name to split and rejoin.
        split_on: Separator that divides `name` into parts.
        join_on: Separator placed between the parts in the result.
        capitalize: Whether to capitalize each part (first letter uppercased,
            remainder lowercased). Defaults to `False`.

    Returns:
        The reformatted name.

    Example:
        >>> reformat_name("do_something", split_on="_", join_on=" ", capitalize=True)
        'Do Something'
    """
    parts = (part for part in name.split(split_on) if part)
    if capitalize:
        parts = (part.capitalize() for part in parts)
    return join_on.join(parts)


def split_on_uppercase(string: str) -> Iterator[str]:
    """Split a string at uppercase letter boundaries.

    Splits just before every ASCII uppercase letter (A-Z). Empty substrings
    produced by the split are omitted.

    Args:
        string: The string to split (e.g., `"MyClassName"`).

    Yields:
        Non-empty substrings, in order. Each substring starts either at the
        beginning of the original string or just before an uppercase letter.

    Examples:
        >>> list(split_on_uppercase("HelloWorld"))
        ['Hello', 'World']
        >>> list(split_on_uppercase("XMLParser"))
        ['X', 'M', 'L', 'Parser']
        >>> list(split_on_uppercase("alllowercase"))
        ['alllowercase']
    """
    return (s for s in re.split(r"(?=[A-Z])", string) if s)
