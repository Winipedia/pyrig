"""Tests module."""

from abc import ABC, abstractmethod

import pytest

from pyrig.src.modules.function import is_abstractmethod
from pyrig.src.testing.assertions import assert_with_info, assert_with_msg


def test_assert_with_msg() -> None:
    """Test func for assert_with_msg."""
    # Test with True expression - should not raise
    assert_with_msg(expr=True, msg="This should not raise")

    # Test with boolean expressions that evaluate to True - should not raise
    assert_with_msg(expr=bool(1), msg="Non-zero number should be truthy")
    assert_with_msg(expr=bool("non-empty"), msg="Non-empty string should be truthy")
    assert_with_msg(expr=bool([1, 2, 3]), msg="Non-empty list should be truthy")
    assert_with_msg(expr=bool({"key": "value"}), msg="Non-empty dict should be truthy")

    # Test with False expression - should raise AssertionError with custom message
    custom_message = "This is a custom error message"
    with pytest.raises(AssertionError, match=custom_message):
        assert_with_msg(expr=False, msg=custom_message)

    # Test with boolean expressions that evaluate to False - should raise AssertionError
    falsy_message = "Falsy value should raise"

    with pytest.raises(AssertionError, match=falsy_message):
        assert_with_msg(expr=bool(0), msg=falsy_message)

    with pytest.raises(AssertionError, match=falsy_message):
        assert_with_msg(expr=bool(""), msg=falsy_message)

    with pytest.raises(AssertionError, match=falsy_message):
        assert_with_msg(expr=bool([]), msg=falsy_message)

    with pytest.raises(AssertionError, match=falsy_message):
        assert_with_msg(expr=bool({}), msg=falsy_message)

    with pytest.raises(AssertionError, match=falsy_message):
        assert_with_msg(expr=bool(None), msg=falsy_message)

    # Test with comparison expressions
    comparison_value = 5
    greater_than_five = 7
    less_than_five = 3
    assert_with_msg(
        expr=greater_than_five > comparison_value,
        msg="Seven should be greater than five",
    )

    comparison_message = "Three should not be greater than five"
    with pytest.raises(AssertionError, match=comparison_message):
        assert_with_msg(expr=less_than_five > comparison_value, msg=comparison_message)

    # Test with function calls
    def always_true() -> bool:
        return True

    def always_false() -> bool:
        return False

    assert_with_msg(expr=always_true(), msg="Function returning True should pass")

    function_message = "Function returning False should fail"
    with pytest.raises(AssertionError, match=function_message):
        assert_with_msg(expr=always_false(), msg=function_message)

    # Test that the function works with variables
    original_expr = True
    original_msg = "Original message"
    assert_with_msg(expr=original_expr, msg=original_msg)

    # Verify the original values are unchanged (they should be immutable anyway)
    assert_with_msg(
        expr=original_expr is True, msg="Original expr should still be True"
    )
    assert_with_msg(
        expr=original_msg == "Original message",
        msg="Original message should be unchanged",
    )


def test_assert_with_info() -> None:
    """Test func for assert_with_info."""
    # Test with True expression - should not raise
    assert_with_info(
        expr=True, expected="True", actual="True", msg="This should not raise"
    )
    # Test with False expression - should raise AssertionError with custom message
    custom_message = "This is a custom error message"
    with pytest.raises(AssertionError, match=custom_message):
        assert_with_info(
            expr=False, expected="True", actual="False", msg=custom_message
        )


def test_assert_isabstrct_method() -> None:
    """Test func for assert_isabstrct_method."""

    class AbstractClass(ABC):
        """Abstract class for testing."""

        @abstractmethod
        def abstract_method(self) -> None:
            pass

        def concrete_method(self) -> None:
            """Concrete method."""
            return

    is_abstract = is_abstractmethod(AbstractClass.abstract_method)
    assert_with_msg(
        is_abstract, "Expected abstract method to be identified as abstract"
    )

    is_abstract = is_abstractmethod(AbstractClass.concrete_method)
    assert_with_msg(
        not is_abstract, "Expected concrete method to not be identified as abstract"
    )
