"""module for the following module path (maybe truncated).

tests.test_pyrig.test_conventions.test_testing
"""

import sys

import pytest

from pyrig.src.testing.convention import (
    TEST_CLASS_PREFIX,
    TEST_FUNCTION_PREFIX,
    TEST_MODULE_PREFIX,
    get_obj_from_test_obj,
    get_right_test_prefix,
    get_test_obj_from_obj,
    make_obj_importpath_from_test_obj,
    make_summary_error_msg,
    make_test_obj_importpath_from_obj,
    make_test_obj_name,
    reverse_make_test_obj_name,
)


# Sample objects for testing
def sample_function() -> None:
    """Sample function for testing."""


class SampleClass:
    """Sample class for testing."""

    def sample_method(self) -> None:
        """Sample method for testing."""


def test_get_right_test_prefix() -> None:
    """Test func for get_right_test_prefix."""
    # Test with a function
    func_prefix = get_right_test_prefix(sample_function)
    assert func_prefix == TEST_FUNCTION_PREFIX, (
        f"Expected {TEST_FUNCTION_PREFIX} for function, got {func_prefix}"
    )

    # Test with a class
    class_prefix = get_right_test_prefix(SampleClass)
    assert class_prefix == TEST_CLASS_PREFIX, (
        f"Expected {TEST_CLASS_PREFIX} for class, got {class_prefix}"
    )

    # Test with a module
    assert get_right_test_prefix(sys) == TEST_MODULE_PREFIX, (
        f"Expected {TEST_MODULE_PREFIX} for module, got {get_right_test_prefix(sys)}"
    )


def test_make_test_obj_name() -> None:
    """Test func for make_test_obj_name."""
    # Test with a function
    expected_func_name = f"{TEST_FUNCTION_PREFIX}{sample_function.__name__}"
    assert make_test_obj_name(sample_function) == expected_func_name, (
        f"Expected {expected_func_name}, got {make_test_obj_name(sample_function)}"
    )

    # Test with a class
    expected_class_name = f"{TEST_CLASS_PREFIX}{SampleClass.__name__}"
    assert make_test_obj_name(SampleClass) == expected_class_name, (
        f"Expected {expected_class_name}, got {make_test_obj_name(SampleClass)}"
    )

    # Test with a module
    expected_module_name = f"{TEST_MODULE_PREFIX}{sys.__name__}"
    assert make_test_obj_name(sys) == expected_module_name, (
        f"Expected {expected_module_name}, got {make_test_obj_name(sys)}"
    )


def test_reverse_make_test_obj_name() -> None:
    """Test func for reverse_make_test_obj_name."""
    # Test with function prefix
    test_func_name = f"{TEST_FUNCTION_PREFIX}{sample_function.__name__}"
    assert reverse_make_test_obj_name(test_func_name) == sample_function.__name__, (
        f"Expected '{sample_function.__name__}', "
        f"got {reverse_make_test_obj_name(test_func_name)}"
    )

    # Test with class prefix
    test_class_name = f"{TEST_CLASS_PREFIX}{SampleClass.__name__}"
    assert reverse_make_test_obj_name(test_class_name) == SampleClass.__name__, (
        f"Expected '{SampleClass.__name__}', "
        f"got {reverse_make_test_obj_name(test_class_name)}"
    )

    # Test with module prefix
    test_module_name = f"{TEST_MODULE_PREFIX}{sys.__name__}"
    assert reverse_make_test_obj_name(test_module_name) == sys.__name__, (
        f"Expected '{sys.__name__}', got {reverse_make_test_obj_name(test_module_name)}"
    )

    # Test with invalid prefix
    with pytest.raises(ValueError, match="is expected to start with one of"):
        reverse_make_test_obj_name("invalid_prefix_name")


def test_make_test_obj_importpath_from_obj() -> None:
    """Test func for make_test_obj_importpath_from_obj."""
    path = make_test_obj_importpath_from_obj(make_test_obj_importpath_from_obj)
    expected = (
        test_make_test_obj_importpath_from_obj.__module__
        + "."
        + test_make_test_obj_importpath_from_obj.__name__
    )
    assert path == expected, f"Expected '{expected}', got {path}"
    expected = (
        test_make_test_obj_importpath_from_obj.__module__
        + "."
        + test_make_test_obj_importpath_from_obj.__name__
    )
    assert path == expected, f"Expected '{expected}', got {path}"


def test_make_obj_importpath_from_test_obj() -> None:
    """Test func for make_obj_importpath_from_test_obj."""
    path = make_obj_importpath_from_test_obj(test_make_obj_importpath_from_test_obj)
    expected = (
        make_obj_importpath_from_test_obj.__module__
        + "."
        + make_obj_importpath_from_test_obj.__name__
    )
    assert path == expected, f"Expected '{expected}', got {path}"
    expected = (
        make_obj_importpath_from_test_obj.__module__
        + "."
        + make_obj_importpath_from_test_obj.__name__
    )
    assert path == expected, f"Expected '{expected}', got {path}"


def test_get_test_obj_from_obj() -> None:
    """Test func for get_test_obj_from_obj."""
    test_obj = get_test_obj_from_obj(get_test_obj_from_obj)
    expected = test_get_test_obj_from_obj
    assert test_obj.__name__ == expected.__name__, (  # ty:ignore[unresolved-attribute]
        f"Expected '{expected}', got {test_obj}"
    )


def test_get_obj_from_test_obj() -> None:
    """Test func for get_obj_from_test_obj."""
    obj = get_obj_from_test_obj(test_get_obj_from_test_obj)
    expected = get_obj_from_test_obj
    assert obj == expected, f"Expected '{expected}', got {obj}"


def test_make_summary_error_msg() -> None:
    """Test func."""
    # Test with empty list
    empty_msg = make_summary_error_msg([])
    assert isinstance(empty_msg, str)

    # Test with one item
    one_item_msg = make_summary_error_msg(["module.function"])
    assert isinstance(one_item_msg, str)

    # Test with multiple items
    items = ["module.function1", "module.class.method", "another_module"]
    multi_item_msg = make_summary_error_msg(items)
    assert isinstance(multi_item_msg, str)

    for item in items:
        assert item in multi_item_msg
