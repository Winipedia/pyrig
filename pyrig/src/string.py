"""String manipulation and naming convention utilities.

Provides utilities for transforming Python identifiers between different case styles
(snake_case, PascalCase, kebab-case) and creating human-readable names from objects.
"""

import re
from collections.abc import Callable
from types import ModuleType
from typing import Any


def split_on_uppercase(string: str) -> list[str]:
    """Split a string at uppercase letter boundaries.

    Splits PascalCase or camelCase identifiers into component words.

    Args:
        string: String to split (e.g., "MyClassName", "parseHTMLDocument").

    Returns:
        List of substrings split before each uppercase letter.
            Empty strings filtered out.

    Note:
        Consecutive uppercase letters are split individually: "XMLParser"
            → ['X', 'M', 'L', 'Parser'].
    """
    return [s for s in re.split(r"(?=[A-Z])", string) if s]


def make_name_from_obj(
    obj: ModuleType | Callable[..., Any] | type | str,
    split_on: str = "_",
    join_on: str = "-",
    *,
    capitalize: bool = True,
) -> str:
    """Create a human-readable name from a Python object or string.

    Transforms Python identifiers into formatted display names. Commonly used for
    generating CLI command names from function names.

    Args:
        obj: Object to extract name from (module, function, class, or string).
        split_on: Character(s) to split on (default: "_").
        join_on: Character(s) to join with (default: "-").
        capitalize: Whether to capitalize each word (default: True).

    Returns:
        Formatted string with parts split and rejoined.

    Raises:
        ValueError: If object has no `__name__` attribute and is not a string.

    Note:
        For non-string objects, only the last component of `__name__` is used.
        Does not handle PascalCase splitting; use `split_on_uppercase` first if needed.
    """
    if not isinstance(obj, str):
        name = getattr(obj, "__name__", "")
        if not name:
            msg = f"Cannot extract name from {obj}"
            raise ValueError(msg)
        obj_name: str = name.split(".")[-1]
    else:
        obj_name = obj
    parts = obj_name.split(split_on)
    if capitalize:
        parts = [part.capitalize() for part in parts]
    return join_on.join(parts)


def re_search_excluding_docstrings(
    pattern: str | re.Pattern[str], content: str
) -> re.Match[str] | None:
    """Search for a pattern in content, excluding triple-quoted docstrings.

    Args:
        pattern: Regex pattern to search for.
        content: Text content to search within.

    Returns:
        Match object if pattern found outside docstrings, None otherwise.
    """
    content = re.sub(r'"""[\s\S]*?"""', "", content)
    content = re.sub(r"'''[\s\S]*?'''", "", content)
    return re.search(pattern, content)
