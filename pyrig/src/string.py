"""String manipulation and naming convention utilities.

Provides utilities for transforming Python identifiers between different case styles
(snake_case, PascalCase, kebab-case) and creating human-readable names from objects.
"""

import re
from collections.abc import Callable
from types import ModuleType
from typing import Any


def split_on_uppercase(string: str) -> list[str]:
    """Split string at uppercase letter boundaries.

    Args:
        string: String to split (e.g., "MyClassName").

    Returns:
        List of substrings split before each uppercase letter (empty strings filtered).

    Note:
        Consecutive uppercase split individually:
            "XMLParser" → ['X', 'M', 'L', 'Parser'].
    """
    return [s for s in re.split(r"(?=[A-Z])", string) if s]


def make_name_from_obj(
    obj: ModuleType | Callable[..., Any] | type | str,
    split_on: str = "_",
    join_on: str = "-",
    *,
    capitalize: bool = True,
) -> str:
    """Create human-readable name from Python object or string.

    Transforms Python identifiers into formatted display names.

    Args:
        obj: Object to extract name from (module, function, class, or string).
        split_on: Character(s) to split on.
        join_on: Character(s) to join with.
        capitalize: Whether to capitalize each word.

    Returns:
        Formatted string.

    Raises:
        ValueError: If object has no `__name__` and is not string.

    Note:
        For non-string objects, only last component of `__name__` used.
        Does not handle PascalCase; use `split_on_uppercase` first if needed.
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
    """Search for pattern in content, excluding triple-quoted docstrings.

    Args:
        pattern: Regex pattern.
        content: Text content.

    Returns:
        Match object if found outside docstrings, None otherwise.
    """
    content = re.sub(r'"""[\s\S]*?"""', "", content)
    content = re.sub(r"'''[\s\S]*?'''", "", content)
    return re.search(pattern, content)


def starts_with_docstring(content: str) -> bool:
    """Check if content starts with a docstring.

    Args:
        content: Text content.

    Returns:
        True if content starts with a docstring, False otherwise.
    """
    first_line = content.split("\n")[0]
    return any(quote in first_line for quote in ('"""', "'''"))
