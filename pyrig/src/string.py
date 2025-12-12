"""String manipulation and naming convention utilities.

This module provides utility functions for string transformations commonly needed
when working with Python naming conventions. It handles conversions between
different case styles (snake_case, PascalCase, kebab-case) and creates
human-readable names from Python objects.

These utilities are particularly useful for:
    - Generating CLI command names from function names
    - Creating display names for classes and modules
    - Parsing and transforming identifiers

Example:
    >>> from pyrig.src.string import split_on_uppercase, make_name_from_obj
    >>> split_on_uppercase("MyClassName")
    ['My', 'Class', 'Name']
    >>> make_name_from_obj("my_function_name")
    'My-Function-Name'
"""

import re
from collections.abc import Callable
from types import ModuleType
from typing import Any


def split_on_uppercase(string: str) -> list[str]:
    """Split a string at uppercase letter boundaries.

    Useful for parsing PascalCase or camelCase identifiers into their
    component words. Empty strings between consecutive uppercase letters
    are filtered out.

    Args:
        string: The string to split, typically in PascalCase or camelCase.

    Returns:
        A list of substrings, each starting with an uppercase letter
        (except possibly the first if the original string started lowercase).

    Example:
        >>> split_on_uppercase("HelloWorld")
        ['Hello', 'World']
        >>> split_on_uppercase("XMLParser")
        ['X', 'M', 'L', 'Parser']
        >>> split_on_uppercase("lowercase")
        ['lowercase']
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

    Args:
        obj: The object to extract a name from. Can be a module, callable,
            class, or string. For non-string objects, uses the last component
            of `__name__` (e.g., "my_module" from "package.my_module").
        split_on: Character(s) to split the name on. Defaults to underscore
            for snake_case input.
        join_on: Character(s) to join the parts with. Defaults to hyphen
            for kebab-case output.
        capitalize: Whether to capitalize each word. When True, produces
            Title-Case output.

    Returns:
        A formatted string with parts split and rejoined according to the
        specified separators.

    Example:
        >>> make_name_from_obj("my_function_name")
        'My-Function-Name'
        >>> make_name_from_obj("my_function", join_on=" ", capitalize=True)
        'My Function'
        >>> import os
        >>> make_name_from_obj(os.path)
        'Path'
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
