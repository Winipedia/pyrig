"""String manipulation and text encoding utilities."""

import re
from collections.abc import Callable, Iterator
from pathlib import Path
from types import ModuleType
from typing import Any

UTF_8_ENCODING = "utf-8"


def read_text_utf8(path: Path) -> str:
    """Read the text content of a file using UTF-8 encoding."""
    return path.read_text(encoding=UTF_8_ENCODING)


def write_text_utf8(path: Path, content: str) -> int:
    """Write text to a file using UTF-8 encoding.

    Returns:
        Number of characters written.
    """
    return path.write_text(content, encoding=UTF_8_ENCODING)


def open_path_with_utf8(path: Path, *args: Any, **kwargs: Any) -> Any:
    """Open a file with UTF-8 encoding.

    Args:
        path: Path to the file to open.
        *args: Positional arguments forwarded to `Path.open`.
        **kwargs: Keyword arguments forwarded to `Path.open`.

    Returns:
        File object returned by `Path.open`.
    """
    return path.open(*args, encoding=UTF_8_ENCODING, **kwargs)


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


def make_name_from_obj(
    obj: ModuleType | Callable[..., Any] | type | str,
    split_on: str = "_",
    join_on: str = "-",
    *,
    capitalize: bool = True,
) -> str:
    """Create a human-readable display name from a Python object or identifier string.

    Extracts the bare name from a module, function, class, or string, splits it
    on the given separator, optionally capitalizes each part, and rejoins the
    parts with the output separator.

    For non-string objects the `__name__` attribute is used. If the name
    contains dots (e.g., a fully qualified module name), only the last component
    is kept.

    Args:
        obj: Source of the name. For modules, functions, or classes the
            `__name__` attribute is used. For strings the value is used
            directly.
        split_on: Character(s) to split the raw name on. Defaults to `"_"`
            for snake_case identifiers.
        join_on: Character(s) to join the resulting parts with. Defaults to
            `"-"` producing kebab-case output.
        capitalize: Whether to capitalize each part (first letter uppercased,
            remainder lowercased). Defaults to `True`.

    Returns:
        Formatted name string. For example, `"init_project"` becomes
        `"Init-Project"` with the default parameters.

    Examples:
        >>> make_name_from_obj("init_project")
        'Init-Project'
        >>> make_name_from_obj("init_project", join_on=" ")
        'Init Project'

    Note:
        Does not split on uppercase letters. To derive a display name from a
        PascalCase identifier, use `split_on_uppercase` on the class name
        first and join the parts into a snake_case string before passing it
        here.
    """
    if not isinstance(obj, str):
        name = getattr(obj, "__name__", str(obj))
        obj_name: str = name.split(".")[-1]
    else:
        obj_name = obj
    parts = (part for part in obj_name.split(split_on) if part)

    if capitalize:
        parts = (part.capitalize() for part in parts)
    return join_on.join(parts)


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


def fstring_var_name(fstring: str) -> str:
    """Extract the variable name from the output of a debug f-string expression."""
    return fstring.split("=", maxsplit=1)[0].strip()
