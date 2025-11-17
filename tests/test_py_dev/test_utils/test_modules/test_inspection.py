"""module for the following module path (maybe truncated).

tests.test_py_dev.test_modules.test_inspection
"""

from py_dev.utils.modules.inspection import (
    get_def_line,
    get_obj_members,
    get_qualname_of_obj,
    get_unwrapped_obj,
    inside_frozen_bundle,
)
from py_dev.utils.testing.assertions import assert_with_msg


def test_get_obj_members() -> None:
    """Test func for get_obj_members."""
    members = get_obj_members(test_get_obj_members)
    expected = ("__name__", test_get_obj_members.__name__)
    assert_with_msg(
        expected in members,
        f"Expected {expected} in members, got {members}",
    )


def test_get_def_line() -> None:
    """Test func for get_def_line."""

    # Test with a function defined in this module
    def test_function() -> None:
        """Test function."""

    line_num = get_def_line(test_function)
    assert_with_msg(
        line_num > 0,
        f"Expected positive integer line number, got {line_num}",
    )

    # Test with a class method
    class TestClass:
        def test_method(self) -> None:
            """Test method."""

        @property
        def test_property(self) -> str:
            """Test property."""
            return "test"

    method_line = get_def_line(TestClass.test_method)
    assert_with_msg(
        method_line > 0,
        f"Expected positive integer line number for method, got {method_line}",
    )

    # Test with a property
    prop_line = get_def_line(TestClass.test_property)
    assert_with_msg(
        prop_line > 0,
        f"Expected positive integer line number for property, got {prop_line}",
    )


def test_inside_frozen_bundle() -> None:
    """Test func for inside_frozen_bundle."""
    result = inside_frozen_bundle()
    assert_with_msg(result is False, f"Expected False, got {result}")


def test_get_qualname_of_obj() -> None:
    """Test func for get_name_of_obj."""

    # Test with a function
    def test_function() -> None:
        pass

    name = get_qualname_of_obj(test_function)
    assert_with_msg(
        name == "test_get_qualname_of_obj.<locals>.test_function",
        f"Expected 'test_function', got {name}",
    )

    # Test with a class
    class TestClass:
        pass

    name = get_qualname_of_obj(TestClass)
    assert_with_msg(
        name == "test_get_qualname_of_obj.<locals>.TestClass",
        f"Expected 'TestClass', got {name}",
    )

    # Test with a method
    class TestClass2:
        def test_method(self) -> None:
            pass

    name = get_qualname_of_obj(TestClass2.test_method)
    assert_with_msg(
        name == "test_get_qualname_of_obj.<locals>.TestClass2.test_method",
        f"Expected 'test_method', got {name}",
    )


def test_get_unwrapped_obj() -> None:
    """Test func for get_unwrapped_obj."""

    # Test with a function
    def test_function() -> None:
        pass

    unwrapped = get_unwrapped_obj(test_function)
    assert_with_msg(
        unwrapped == test_function, f"Expected {test_function}, got {unwrapped}"
    )

    # Test with a class method
    class TestClass:
        def test_method(self) -> None:
            pass

    unwrapped = get_unwrapped_obj(TestClass.test_method)
    assert_with_msg(
        unwrapped == TestClass.test_method,
        f"Expected {TestClass.test_method}, got {unwrapped}",
    )

    # Test with a property
    class TestClass2:
        @property
        def test_property(self) -> str:
            return "test"

    unwrapped = get_unwrapped_obj(TestClass2.test_property)
    assert_with_msg(
        unwrapped.__name__ == "test_property",
        f"Expected 'test_property', got {unwrapped.__name__}",
    )
