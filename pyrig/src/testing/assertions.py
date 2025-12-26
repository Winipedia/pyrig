"""Testing assertion utilities for enhanced test validation.

This module provides custom assertion functions that extend Python's built-in
assert statement with additional features like improved error messages and
specialized validation logic for common testing scenarios.

The assertions are designed to provide clear, actionable error messages when
tests fail, making it easier to diagnose and fix issues.

Example:
    >>> from pyrig.src.testing.assertions import assert_with_msg, assert_with_info
    >>> # Basic assertion with custom message
    >>> assert_with_msg(2 + 2 == 4, "Math is broken!")
    >>>
    >>> # Assertion with expected/actual comparison
    >>> result = calculate_something()
    >>> assert_with_info(
    ...     result == 42,
    ...     expected=42,
    ...     actual=result,
    ...     msg="Calculation failed"
    ... )

See Also:
    pyrig.src.testing.convention: Test naming conventions
    pytest: The test framework these utilities support
"""

from typing import Any


def assert_with_msg(expr: bool, msg: str) -> None:  # noqa: FBT001
    """Assert that an expression is true with a custom error message.

    A thin wrapper around Python's built-in assert statement that makes it
    easier to provide meaningful error messages when assertions fail. This
    is particularly useful when the default assertion error message doesn't
    provide enough context.

    Args:
        expr: The expression to evaluate for truthiness. Should be a boolean
            expression that evaluates to True if the assertion passes.
        msg: The error message to display if the assertion fails. Should be
            descriptive and actionable, explaining what went wrong and
            potentially how to fix it.

    Raises:
        AssertionError: If the expression evaluates to False. The error
            message will be the provided `msg` parameter.

    Example:
        Basic usage::

            >>> assert_with_msg(len(items) > 0, "Items list cannot be empty")

        With complex conditions::

            >>> assert_with_msg(
            ...     user.is_authenticated and user.has_permission("admin"),
            ...     "User must be authenticated admin to access this resource"
            ... )

    Note:
        This function is marked with security linters (noqa, nosec) because
        assert statements can be optimized away in production code. However,
        this is acceptable for test code where assertions should always run.

    See Also:
        assert_with_info: Enhanced assertion with expected/actual comparison
    """
    assert expr, msg  # noqa: S101  # nosec: B101


def assert_with_info(expr: bool, expected: Any, actual: Any, msg: str = "") -> None:  # noqa: FBT001
    """Assert that an expression is true with expected/actual value comparison.

    Wraps around `assert_with_msg` and adds the expected and actual values to
    the error message. This provides a clear comparison when the assertion
    fails, making it immediately obvious what the test expected versus what
    it actually received.

    The error message format is:
        Expected: <expected>
        Actual: <actual>
        <msg>

    Args:
        expr: The expression to evaluate for truthiness. Typically a comparison
            between `expected` and `actual` (e.g., `actual == expected`).
        expected: The expected value. This is what the test anticipated the
            result would be.
        actual: The actual value. This is what the code actually produced.
        msg: Optional additional context to include in the error message.
            Defaults to an empty string.

    Raises:
        AssertionError: If the expression evaluates to False. The error
            message will include the expected value, actual value, and any
            additional message provided.

    Example:
        Basic usage::

            >>> result = calculate_sum(2, 2)
            >>> assert_with_info(result == 4, expected=4, actual=result)

        With additional context::

            >>> result = fetch_user_count()
            >>> assert_with_info(
            ...     result == 100,
            ...     expected=100,
            ...     actual=result,
            ...     msg="Database should have exactly 100 test users"
            ... )

        With complex objects::

            >>> expected_config = {"debug": True, "port": 8000}
            >>> actual_config = load_config()
            >>> assert_with_info(
            ...     actual_config == expected_config,
            ...     expected=expected_config,
            ...     actual=actual_config,
            ...     msg="Configuration mismatch"
            ... )

    Note:
        The expected and actual values are converted to strings for display,
        so they should have meaningful `__repr__` or `__str__` implementations
        for best results.

    See Also:
        assert_with_msg: Basic assertion with custom message
    """
    msg = f"""
Expected: {expected}
Actual: {actual}
{msg}
"""
    assert_with_msg(expr, msg)
