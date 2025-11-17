"""String utilities."""

import re
from collections.abc import Callable
from types import ModuleType
from typing import Any


def split_on_uppercase(string: str) -> list[str]:
    """Split a string on uppercase letters.

    Args:
        string: String to split

    Returns:
        List of substrings split on uppercase letters

    Example:
        split_on_uppercase("HelloWorld") -> ["Hello", "World"]

    """
    return [s for s in re.split(r"(?=[A-Z])", string) if s]


def make_name_from_obj(
    package: ModuleType | Callable[..., Any] | type | str,
    split_on: str = "_",
    join_on: str = "-",
    *,
    capitalize: bool = True,
) -> str:
    """Make a name from a package.

    takes a package and makes a name from it that is readable by humans.

    Args:
        package (ModuleType): The package to make a name from
        split_on (str, optional): what to split the package name on. Defaults to "_".
        join_on (str, optional): what to join the package name with. Defaults to "-".
        capitalize (bool, optional): Whether to capitalize each part. Defaults to True.

    Returns:
        str: _description_
    """
    if not isinstance(package, str):
        package_name = package.__name__.split(".")[-1]
    else:
        package_name = package
    parts = package_name.split(split_on)
    if capitalize:
        parts = [part.capitalize() for part in parts]
    return join_on.join(parts)
