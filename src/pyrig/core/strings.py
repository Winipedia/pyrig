"""String manipulation utilities.

Provides functions for common string transformations used throughout pyrig,
including file I/O with consistent encoding, case conversions between naming
conventions, regex patterns for parsing, human-readable name generation,
and formatted output helpers.
"""

import re
from collections.abc import Callable, Iterable, Iterator
from pathlib import Path
from types import ModuleType
from typing import Any

UTF_8_ENCODING = "utf-8"


def read_text_utf8(path: Path) -> str:
    """Read the text content of a file using UTF-8 encoding.

    Prefer this over calling ``Path.read_text`` directly to ensure consistent
    UTF-8 encoding is used across the entire codebase.

    Args:
        path: Path to the file to read.

    Returns:
        File content as a string.
    """
    return path.read_text(encoding=UTF_8_ENCODING)


def write_text_utf8(path: Path, content: str) -> int:
    """Write text to a file using UTF-8 encoding.

    Prefer this over calling ``Path.write_text`` directly to ensure consistent
    UTF-8 encoding is used across the entire codebase.

    Args:
        path: Path to the file to write.
        content: Text content to write.

    Returns:
        Number of characters written.
    """
    return path.write_text(content, encoding=UTF_8_ENCODING)


def open_path_with_utf8(path: Path, *args: Any, **kwargs: Any) -> Any:
    """Open a file with UTF-8 encoding.

    Args:
        path: Path to the file to open.
        *args: Positional arguments to pass to `open`.
        **kwargs: Keyword arguments to pass to `open`.

    Returns:
        File object.
    """
    return path.open(*args, encoding=UTF_8_ENCODING, **kwargs)


def file_has_content(path: Path) -> bool:
    """Check whether a file has non-empty content.

    Args:
        path: Path to the file to check.

    Returns:
        ``True`` if the file has non-empty content; ``False`` if the file is
        empty (zero bytes).

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    return path.stat().st_size > 0


def kebab_to_snake_case(value: str) -> str:
    """Convert a kebab-case string to snake_case by replacing hyphens with underscores.

    Args:
        value: A kebab-case string (e.g., ``"my-project"``).

    Returns:
        The snake_case equivalent (e.g., ``"my_project"``).
    """
    return value.replace("-", "_")


def snake_to_kebab_case(value: str) -> str:
    """Convert a snake_case string to kebab-case by replacing underscores with hyphens.

    Args:
        value: A snake_case string (e.g., ``"my_project"``).

    Returns:
        The kebab-case equivalent (e.g., ``"my-project"``).
    """
    return value.replace("_", "-")


def split_on_uppercase(string: str) -> Iterator[str]:
    """Split a string at uppercase letter boundaries.

    Uses a zero-width lookahead regex to split just before every ASCII uppercase
    letter (A-Z). Empty strings produced by the split are filtered out.

    Args:
        string: The string to split (e.g., ``"MyClassName"``).

    Returns:
        Iterator of non-empty substrings. Each substring starts either at the
        beginning of the original string or just before an uppercase letter.

    Example:
        >>> list(split_on_uppercase("HelloWorld"))
        ['Hello', 'World']
        >>> list(split_on_uppercase("XMLParser"))
        ['X', 'M', 'L', 'Parser']
        >>> list(split_on_uppercase("alllowercase"))
        ['alllowercase']
    """
    return (s for s in re.split(r"(?=[A-Z])", string) if s)


def dependency_requirement_split_pattern() -> re.Pattern[str]:
    """Return a compiled regex pattern that matches non-package-name characters.

    The pattern matches any character that is not alphanumeric, an underscore,
    a hyphen, or a period. When used with ``re.Pattern.split``, the first
    element of the result is the bare package name, stripped of version
    specifiers and any extras notation.

    For example, calling ``pattern.split("requests>=2.0,<3.0", maxsplit=1)``
    yields ``["requests", "=2.0,<3.0"]``, so ``result[0]`` is ``"requests"``.
    Calling ``pattern.split("requests[security]>=2.0", maxsplit=1)``
    yields ``["requests", "security]>=2.0"]``, so extras are stripped from
    ``result[0]``.

    Returns:
        Compiled regex pattern matching characters outside a valid package name.
    """
    # re.compile is already internally cached by Python
    return re.compile(r"[^a-zA-Z0-9_.-]")


def dependency_requirement_as_package_name(dep_req: str) -> str:
    """Extract the package name from a dependency requirement string.

    Uses the split pattern to separate the package name from any version specifiers
    or other extraneous characters. The resulting package name is converted from
    kebab-case to snake_case to match Python package naming conventions.

    Args:
        dep_req: A dependency requirement string (e.g., ``"requests>=2.0,<3.0"`` or
            ``"my-package[extra]==1.0.0"``).

    Returns:
        The package name in snake_case (e.g., ``"requests"`` or ``"my_package"``).
    """
    return kebab_to_snake_case(
        dependency_requirement_split_pattern().split(dep_req, maxsplit=1)[0]
    )


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

    For non-string objects the ``__name__`` attribute is used. If the name
    contains dots (e.g., a fully qualified module name), only the last component
    is kept.

    Args:
        obj: Source of the name. For modules, functions, or classes the
            ``__name__`` attribute is used. For strings the value is used
            directly.
        split_on: Character(s) to split the raw name on. Defaults to ``"_"``
            for snake_case identifiers.
        join_on: Character(s) to join the resulting parts with. Defaults to
            ``"-"`` producing kebab-case output.
        capitalize: Whether to capitalize each part (first letter uppercased,
            remainder lowercased). Defaults to ``True``.

    Returns:
        Formatted name string. For example, ``"init_project"`` becomes
        ``"Init-Project"`` with the default parameters.

    Example:
        >>> make_name_from_obj("init_project")
        'Init-Project'
        >>> make_name_from_obj("init_project", join_on=" ")
        'Init Project'

    Note:
        This function does not split on uppercase letters. To derive a display
        name from a PascalCase identifier, use ``split_on_uppercase`` on the
        class name first and join the parts into a snake_case string before
        passing it here.
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


def make_summary_error_msg(
    paths: Iterable[Path],
) -> str:
    """Create a formatted multi-line error message listing file locations.

    Produces a human-readable summary intended for use in assertion error
    messages when multiple validation failures are detected across the codebase.

    Args:
        paths: File paths where errors were found.

    Returns:
        A string containing ``"Found errors at:"`` followed by each path
        on its own line, prefixed with ``"- "``.
    """
    msg = """
Found errors at:
"""
    for error_location in paths:
        msg += f"""
- {error_location}"""
    return msg


def make_linked_badge_markdown(
    badge_url: str,
    link_url: str,
    alt_text: str,
) -> str:
    """Return Markdown for a clickable badge image.

    Args:
        badge_url: URL of the badge image.
        link_url: URL the badge should link to when clicked.
        alt_text: Alternative text for the image (used for accessibility).

    Returns:
        Markdown string in the form ``[![alt_text](badge_url)](link_url)``.
    """
    return f"[![{alt_text}]({badge_url})]({link_url})"
