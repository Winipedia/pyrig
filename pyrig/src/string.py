"""String manipulation and naming convention utilities.

This module provides utility functions for string transformations commonly needed
when working with Python naming conventions. It handles conversions between
different case styles (snake_case, PascalCase, kebab-case) and creates
human-readable names from Python objects.

These utilities are particularly useful for:
    - Generating CLI command names from function names
    - Creating display names for classes and modules
    - Parsing and transforming identifiers
    - Converting between naming conventions

Example:
    >>> from pyrig.src.string import split_on_uppercase, make_name_from_obj
    >>> split_on_uppercase("MyClassName")
    ['My', 'Class', 'Name']
    >>> make_name_from_obj("my_function_name")
    'My-Function-Name'

See Also:
    pyrig.src.cli: CLI utilities for project name extraction
    pyrig.src.modules.package: Package naming utilities
"""

import re
from collections.abc import Callable
from types import ModuleType
from typing import Any


def split_on_uppercase(string: str) -> list[str]:
    """Split a string at uppercase letter boundaries.

    Parses PascalCase or camelCase identifiers into their component words by
    splitting before each uppercase letter. Empty strings between consecutive
    uppercase letters are filtered out.

    This is useful for parsing class names, converting PascalCase to other
    formats, or extracting words from compound identifiers.

    Args:
        string: The string to split, typically in PascalCase or camelCase
            format (e.g., "MyClassName", "parseHTMLDocument").

    Returns:
        A list of substrings, each starting with an uppercase letter (except
        possibly the first if the original string started lowercase). Empty
        strings are filtered out.

    Example:
        Basic PascalCase splitting::

            >>> split_on_uppercase("HelloWorld")
            ['Hello', 'World']

        Consecutive uppercase letters (acronyms)::

            >>> split_on_uppercase("XMLParser")
            ['X', 'M', 'L', 'Parser']
            >>> split_on_uppercase("parseHTMLDocument")
            ['parse', 'H', 'T', 'M', 'L', 'Document']

        Lowercase strings (no splitting)::

            >>> split_on_uppercase("lowercase")
            ['lowercase']

        Empty and single-character strings::

            >>> split_on_uppercase("")
            []
            >>> split_on_uppercase("A")
            ['A']

    Note:
        Consecutive uppercase letters are split into individual characters.
        For example, "XMLParser" becomes ['X', 'M', 'L', 'Parser'], not
        ['XML', 'Parser']. This is a limitation of the simple regex approach.

    See Also:
        make_name_from_obj: Convert objects to formatted names
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

    Transforms Python identifiers (typically in snake_case) into formatted
    display names. Commonly used to generate CLI command names, display
    labels, or documentation titles from function/class/module names.

    The function extracts the name from the object (using `__name__`), takes
    the last component (after the last dot), splits it on the specified
    separator, optionally capitalizes each part, and joins with a new separator.

    Args:
        obj: The object to extract a name from. Can be:
            - **Module**: Uses `module.__name__` (e.g., `os.path` → "path")
            - **Function/Method**: Uses `func.__name__` (e.g., `my_func` → "my_func")
            - **Class**: Uses `cls.__name__` (e.g., `MyClass` → "MyClass")
            - **String**: Used directly as the name
        split_on: Character(s) to split the name on. Defaults to underscore
            ("_") for snake_case input. Can be any string (e.g., ".", "-").
        join_on: Character(s) to join the parts with. Defaults to hyphen
            ("-") for kebab-case output. Can be any string (e.g., " ", "_").
        capitalize: Whether to capitalize each word. When True, produces
            Title-Case output (e.g., "My-Function-Name"). When False, preserves
            original casing.

    Returns:
        A formatted string with parts split and rejoined according to the
        specified separators and capitalization.

    Raises:
        ValueError: If the object has no `__name__` attribute and is not a string.

    Example:
        Basic usage with snake_case function names::

            >>> make_name_from_obj("my_function_name")
            'My-Function-Name'

        Custom separators::

            >>> make_name_from_obj("my_function", join_on=" ", capitalize=True)
            'My Function'
            >>> make_name_from_obj("my.module.name", split_on=".", join_on="-")
            'Name'  # Only last component is used

        With Python objects::

            >>> import os
            >>> make_name_from_obj(os.path)
            'Path'

            >>> def my_cli_command():
            ...     pass
            >>> make_name_from_obj(my_cli_command)
            'My-Cli-Command'

        Without capitalization::

            >>> make_name_from_obj("my_function", capitalize=False)
            'my-function'

    Note:
        - For non-string objects, only the last component of `__name__` is used
          (after splitting on "."). For example, "package.module.function" becomes
          "function".
        - The function does not handle PascalCase splitting. Use `split_on_uppercase`
          first if you need to split PascalCase names.

    See Also:
        split_on_uppercase: Split PascalCase strings
        pyrig.src.cli.get_project_name_from_argv: Extract project name from CLI
        pyrig.src.modules.package.get_pkg_name_from_project_name: Convert project
            name to package name
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

    Removes all triple-quoted string blocks from the content
    before performing the regex search. This prevents false positives when
    searching for patterns that might appear in documentation.

    Args:
        pattern: Regex pattern to search for (string or compiled pattern).
        content: Text content to search within.

    Returns:
        Match object if pattern is found outside docstrings, None otherwise.
    """
    content = re.sub(r'"""[\s\S]*?"""', "", content)
    content = re.sub(r"'''[\s\S]*?'''", "", content)
    return re.search(pattern, content)
