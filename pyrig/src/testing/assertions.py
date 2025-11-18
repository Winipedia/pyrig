"""Testing assertion utilities for enhanced test validation.

This module provides custom assertion functions that extend Python's built-in
assert statement with additional features like improved error messages and
specialized validation logic for common testing scenarios.
"""

from typing import Any

from pyrig.src.modules.function import is_abstractmethod


def assert_with_msg(expr: bool, msg: str) -> None:  # noqa: FBT001
    """Assert that an expression is true with a custom error message.

    A thin wrapper around Python's built-in assert statement that makes it
    easier to provide meaningful error messages when assertions fail.

    Args:
        expr: The expression to evaluate for truthiness
        msg: The error message to display if the assertion fails

    Raises:
        AssertionError: If the expression evaluates to False

    """
    assert expr, msg  # noqa: S101  # nosec: B101


def assert_with_info(expr: bool, expected: Any, actual: Any, msg: str = "") -> None:  # noqa: FBT001
    """Assert that an expression is true with a custom error message.

    wraps around assert with msg and adds the expected and actual values to the message.

    Args:
        expr: The expression to evaluate for truthiness
        expected: The expected value
        actual: The actual value
        msg: The error message to display if the assertion fails

    Raises:
        AssertionError: If the expression evaluates to False

    """
    msg = f"""
Expected: {expected}
Actual: {actual}
{msg}
"""
    assert_with_msg(expr, msg)


def assert_isabstrct_method(method: Any) -> None:
    """Assert that a method is an abstract method.

    Args:
        method: The method to check

    Raises:
        AssertionError: If the method is not an abstract method

    """
    assert_with_msg(
        is_abstractmethod(method),
        f"Expected {method} to be abstract method",
    )
