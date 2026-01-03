"""module for the following module path (maybe truncated).

tests.test_pyrig.test_modules.test_inspection
"""

import os

from pyrig.src.modules.inspection import (
    get_def_line,
    get_module_of_obj,
    get_obj_members,
    get_qualname_of_obj,
    get_unwrapped_obj,
    inside_frozen_bundle,
)


def test_get_obj_members() -> None:
    """Test func for get_obj_members."""
    members = get_obj_members(test_get_obj_members)
    assert isinstance(members, list), f"Expected list, got {type(members)}"
    assert len(members) > 0, f"Expected at least 1 member, got {len(members)}"


def test_get_def_line() -> None:
    """Test func for get_def_line."""

    # Test with a function defined in this module
    def test_function() -> None:
        """Test function."""

    line_num = get_def_line(test_function)
    assert line_num > 0, f"Expected positive integer line number, got {line_num}"

    # Test with a class method
    class TestClass:
        def test_method(self) -> None:
            """Test method."""

        @property
        def test_property(self) -> str:
            """Test property."""
            return "test"

    method_line = get_def_line(TestClass.test_method)
    assert method_line > 0, (
        f"Expected positive integer line number for method, got {method_line}"
    )

    # Test with a property
    prop_line = get_def_line(TestClass.test_property)
    assert prop_line > 0, (
        f"Expected positive integer line number for property, got {prop_line}"
    )


def test_inside_frozen_bundle() -> None:
    """Test func for inside_frozen_bundle."""
    result = inside_frozen_bundle()
    assert result is False, f"Expected False, got {result}"


def test_get_qualname_of_obj() -> None:
    """Test func for get_name_of_obj."""

    # Test with a function
    def test_function() -> None:
        pass

    name = get_qualname_of_obj(test_function)
    assert name == "test_get_qualname_of_obj.<locals>.test_function", (
        f"Expected 'test_function', got {name}"
    )

    # Test with a class
    class TestClass:
        pass

    name = get_qualname_of_obj(TestClass)
    assert name == "test_get_qualname_of_obj.<locals>.TestClass", (
        f"Expected 'TestClass', got {name}"
    )

    # Test with a method
    class TestClass2:
        def test_method(self) -> None:
            pass

    name = get_qualname_of_obj(TestClass2.test_method)
    assert name == "test_get_qualname_of_obj.<locals>.TestClass2.test_method", (
        f"Expected 'test_method', got {name}"
    )


def test_get_unwrapped_obj() -> None:
    """Test func for get_unwrapped_obj."""

    # Test with a function
    def test_function() -> None:
        pass

    unwrapped = get_unwrapped_obj(test_function)
    assert unwrapped == test_function, f"Expected {test_function}, got {unwrapped}"

    # Test with a class method
    class TestClass:
        def test_method(self) -> None:
            pass

    unwrapped = get_unwrapped_obj(TestClass.test_method)
    assert unwrapped == TestClass.test_method, (
        f"Expected {TestClass.test_method}, got {unwrapped}"
    )

    # Test with a property
    class TestClass2:
        @property
        def test_property(self) -> str:
            return "test"

    unwrapped = get_unwrapped_obj(TestClass2.test_property)
    assert unwrapped.__name__ == "test_property", (
        f"Expected 'test_property', got {unwrapped.__name__}"
    )


def test_get_module_of_obj() -> None:
    """Test func for get_module_of_obj."""

    # Test with a function
    def test_function() -> None:
        pass

    module = get_module_of_obj(test_function)
    assert module.__name__ == __name__, (
        f"Expected module name {__name__}, got {module.__name__}"
    )

    # Test with a class method
    class TestClass:
        def test_method(self) -> None:
            pass

        @property
        def test_property(self) -> str:
            return "test"

    method_module = get_module_of_obj(TestClass.test_method)
    assert method_module.__name__ == __name__, (
        f"Expected module name {__name__}, got {method_module.__name__}"
    )

    # Test with a property
    prop_module = get_module_of_obj(TestClass.test_property)
    assert prop_module.__name__ == __name__, (
        f"Expected module name {__name__}, got {prop_module.__name__}"
    )

    # Test with built-in function
    os_module = get_module_of_obj(os.path.join)
    assert "posixpath" in os_module.__name__ or "ntpath" in os_module.__name__, (
        f"Expected posixpath or ntpath module, got {os_module.__name__}"
    )
