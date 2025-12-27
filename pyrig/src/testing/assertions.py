"""Testing assertion utilities.

Custom assertion functions with enhanced error messages for test validation.

Example:
    >>> from pyrig.src.testing.assertions import assert_with_msg, assert_with_info
    >>> assert_with_msg(2 + 2 == 4, "Math is broken!")
    >>> assert_with_info(result == 42, expected=42, actual=result)
"""

from typing import Any


def assert_with_msg(expr: bool, msg: str) -> None:  # noqa: FBT001
    """Assert expression is true with custom error message.

    Wrapper around assert statement for meaningful error messages.

    Args:
        expr: Boolean expression to evaluate.
        msg: Error message if assertion fails.

    Raises:
        AssertionError: If expression evaluates to False.

    Example:
        >>> assert_with_msg(len(items) > 0, "Items list cannot be empty")
    """
    assert expr, msg  # noqa: S101  # nosec: B101


def assert_with_info(expr: bool, expected: Any, actual: Any, msg: str = "") -> None:  # noqa: FBT001
    """Assert expression is true with expected/actual value comparison.

    Adds expected and actual values to error message for clear comparison.

    Args:
        expr: Boolean expression to evaluate (typically actual == expected).
        expected: Expected value.
        actual: Actual value.
        msg: Optional additional context.

    Raises:
        AssertionError: If expression evaluates to False.

    Example:
        >>> assert_with_info(result == 4, expected=4, actual=result)
    """
    msg = f"""
Expected: {expected}
Actual: {actual}
{msg}
"""
    assert_with_msg(expr, msg)
