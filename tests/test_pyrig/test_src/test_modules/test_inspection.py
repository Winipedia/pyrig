"""module for the following module path (maybe truncated).

tests.test_pyrig.test_modules.test_inspection
"""

import os
from collections.abc import Callable
from functools import wraps

from pyrig.src.modules.inspection import (
    get_def_line,
    get_module_of_obj,
    get_obj_members,
    get_qualname_of_obj,
    get_unwrapped_obj,
    inside_frozen_bundle,
)


def test_get_obj_members() -> None:
    """Test function."""
    members = get_obj_members(test_get_obj_members)
    assert isinstance(members, list), f"Expected list, got {type(members)}"
    assert len(members) > 0, f"Expected at least 1 member, got {len(members)}"


def test_get_def_line() -> None:
    """Test function."""

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
    """Test function."""
    result = inside_frozen_bundle()
    assert result is False, f"Expected False, got {result}"


def test_get_qualname_of_obj() -> None:
    """Test function."""

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


def _dec_a[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return func(*args, **kwargs)

    return wrapper


def _dec_b[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return func(*args, **kwargs)

    return wrapper


def _dec_c[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return func(*args, **kwargs)

    return wrapper


@_dec_a
@_dec_b
@_dec_c
def _deeply_decorated_func() -> str:
    return "deep"


class _TestDeeplyNestedClassMethod:
    @classmethod
    @_dec_a
    @_dec_b
    @_dec_c
    def deeply_nested_class_method(cls) -> str:
        return "deeply_nested"


def test_get_unwrapped_obj() -> None:
    """Test function."""
    unwrapped_func = get_unwrapped_obj(_deeply_decorated_func)
    assert unwrapped_func.__name__ == "_deeply_decorated_func", (
        f"Expected '_deeply_decorated_func', got {unwrapped_func.__name__}"
    )

    unwrapped_method = get_unwrapped_obj(
        _TestDeeplyNestedClassMethod.deeply_nested_class_method
    )
    assert unwrapped_method.__name__ == "deeply_nested_class_method", (
        f"Expected 'deeply_nested_class_method', got {unwrapped_method.__name__}"
    )


def test_get_module_of_obj() -> None:
    """Test function."""

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
