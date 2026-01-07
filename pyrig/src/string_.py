"""String manipulation and naming convention utilities.

Provides utilities for transforming Python identifiers between different case styles
(snake_case, PascalCase, kebab-case) and creating human-readable names from objects.

These utilities are used throughout pyrig for:
    - Deriving filenames from class names (via `split_on_uppercase`)
    - Generating workflow and CLI command names from Python identifiers
    - Searching code while ignoring documentation strings
    - Formatting multi-location error messages for test fixtures
"""

import re
from collections.abc import Callable, Iterable
from types import ModuleType
from typing import Any


def split_on_uppercase(string: str) -> list[str]:
    """Split string at uppercase letter boundaries.

    Used internally by pyrig to convert PascalCase class names to snake_case
    filenames and to generate human-readable workflow names from class names.

    Args:
        string: String to split (e.g., "MyClassName").

    Returns:
        List of substrings split before each uppercase letter, with empty strings
        filtered out.

    Example:
        >>> split_on_uppercase("HelloWorld")
        ['Hello', 'World']
        >>> split_on_uppercase("XMLParser")
        ['X', 'M', 'L', 'Parser']

    Note:
        Consecutive uppercase letters split individually. Only splits on ASCII
        uppercase letters (A-Z), not Unicode uppercase characters.
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

    Transforms Python identifiers (typically snake_case) into formatted display
    names. Used by pyrig for generating CLI command names, workflow step names,
    and test class names from Python objects.

    Args:
        obj: Object to extract name from (module, function, class, or string).
            For non-string objects, the ``__name__`` attribute is used.
        split_on: Character(s) to split the name on. Defaults to "_" for
            snake_case identifiers.
        join_on: Character(s) to join the parts with. Defaults to "-" for
            kebab-case output.
        capitalize: Whether to capitalize each word in the result.

    Returns:
        Formatted string with parts joined by ``join_on``. For example,
        "some_function" becomes "Some-Function" with default parameters.

    Raises:
        ValueError: If object has no ``__name__`` attribute and is not a string,
            or if the resulting name would be empty or contain only separators.

    Example:
        >>> import my_module
        >>> make_name_from_obj(my_module)  # __name__ is "my_module"
        'My-Module'
        >>> make_name_from_obj("init_project", join_on=" ")
        'Init Project'

    Note:
        For non-string objects, only the last component of ``__name__`` is used
        (e.g., "package.submodule" → "submodule"). Does not handle PascalCase
        identifiers; use `split_on_uppercase` first if needed.
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
    # Filter out empty parts to avoid names consisting only of separators
    parts = [part for part in parts if part]
    if not parts:
        msg = f"Cannot create name from '{obj_name}': no valid parts after splitting"
        raise ValueError(msg)
    if capitalize:
        parts = [part.capitalize() for part in parts]
    return join_on.join(parts)


def re_search_excluding_docstrings(
    pattern: str | re.Pattern[str], content: str
) -> re.Match[str] | None:
    """Search for regex pattern in Python source code, excluding docstrings.

    Used by pyrig's test fixtures to detect forbidden patterns (e.g., unittest
    usage) in source code without false positives from documentation strings.

    Args:
        pattern: Regex pattern (string or compiled Pattern object) to search for.
        content: Python source code as a string.

    Returns:
        Match object if pattern is found outside of triple-quoted strings,
        None if not found or only found within docstrings.

    Warning:
        Match positions (``span()``, ``start()``, ``end()``) reference the
        stripped content where docstrings have been removed, not the original.
        Do not use these positions for slicing or indexing the original content.

    Note:
        Removes all triple-quoted strings (both ``\"\"\"`` and ``'''``) using
        regex heuristics. Cannot distinguish docstrings from triple-quoted
        string literals used for other purposes. Unclosed triple-quoted strings
        are not removed, so their content will be searched.
    """
    content = re.sub(r'"""[\s\S]*?"""', "", content)
    content = re.sub(r"'''[\s\S]*?'''", "", content)
    return re.search(pattern, content)


def make_summary_error_msg(
    errors_locations: Iterable[str],
) -> str:
    """Create indented error message summarizing multiple error locations.

    Used by pyrig's test fixtures to format assertion error messages when
    multiple validation failures are detected across the codebase.

    Args:
        errors_locations: Collection of error location strings (e.g., file paths,
            test identifiers, or descriptive location strings).

    Returns:
        Multiline string with "Found errors at:" header and indented bulleted
        list. The output includes leading and trailing whitespace for embedding
        in larger error messages.

    Note:
        The output format is designed for use in assertion messages and includes
        indentation suitable for multiline f-strings. Each location appears on
        its own line with a "- " prefix.
    """
    msg = """
    Found errors at:
    """
    for error_location in errors_locations:
        msg += f"""
        - {error_location}
        """
    return msg
