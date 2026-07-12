"""String manipulation and text encoding utilities."""

import re
from collections.abc import Iterator
from pathlib import Path
from typing import Any

UTF_8_ENCODING = "utf-8"


def file_has_content(path: Path) -> bool:
    """Check whether a file has non-empty content.

    Args:
        path: Path to the file to check.

    Returns:
        `True` if the file has non-empty content; `False` if the file is
        empty (zero bytes).

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    return path.stat().st_size > 0


def open_path_with_utf8(path: Path, *args: Any, **kwargs: Any) -> Any:
    """Open a file with UTF-8 encoding.

    Args:
        path: Path to the file to open.
        *args: Additional positional arguments for opening the file.
        **kwargs: Additional keyword arguments for opening the file.

    Returns:
        The opened file object.
    """
    return path.open(*args, encoding=UTF_8_ENCODING, **kwargs)


def read_text_utf8(path: Path) -> str:
    """Read the text content of a file using UTF-8 encoding.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    return path.read_text(encoding=UTF_8_ENCODING)


def write_text_utf8(path: Path, content: str) -> int:
    """Write `content` to `path` as UTF-8, replacing any existing file.

    Returns:
        The number of characters written.
    """
    return path.write_text(content, encoding=UTF_8_ENCODING)


def fstring_var_name(fstring: str) -> str:
    """Extract the variable name from the output of a debug f-string expression."""
    return fstring.split("=", maxsplit=1)[0].strip()


def is_multiline(string: str) -> bool:
    """Check if a string contains one or more newline characters.

    Args:
        string: The string to check.

    Returns:
        `True` if the string contains at least one newline character; `False` otherwise.
    """
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
