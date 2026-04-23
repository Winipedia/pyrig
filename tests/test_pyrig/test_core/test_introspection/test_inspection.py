"""module for the following module path (maybe truncated).

tests.test_pyrig.test_modules.test_inspection
"""

import os
from collections.abc import Callable
from functools import wraps

import pytest

from pyrig.core.introspection.inspection import (
    def_line,
    obj_members,
    obj_module,
    obj_qualname,
    unwrapped_obj,
)
from pyrig.core.iterate import generator_length


def test_obj_members() -> None:
    """Test function."""
    members = obj_members(test_obj_members)
    assert generator_length(members) > 0


def test_def_line() -> None:
    """Test function."""

    # Test with a function defined in this module
    def test_function() -> None:
        """Test function."""

    line_num = def_line(test_function)
    assert line_num > 0, f"Expected positive integer line number, got {line_num}"

    # Test with a class method
    class TestClass:
        def test_method(self) -> None:
            """Test method."""

        @property
        def test_property(self) -> str:
            """Test property."""
            return "test"

    method_line = def_line(TestClass.test_method)
    assert method_line > 0, (
        f"Expected positive integer line number for method, got {method_line}"
    )

    # Test with a property
    prop_line = def_line(TestClass.test_property)
    assert prop_line > 0, (
        f"Expected positive integer line number for property, got {prop_line}"
    )


def test_obj_qualname() -> None:
    """Test function."""

    # Test with a function
    def test_function() -> None:
        pass

    name = obj_qualname(test_function)
    assert name == "test_obj_qualname.<locals>.test_function", (
        f"Expected 'test_function', got {name}"
    )

    # Test with a class
    class TestClass:
        pass

    name = obj_qualname(TestClass)
    assert name == "test_obj_qualname.<locals>.TestClass", (
        f"Expected 'TestClass', got {name}"
    )

    # Test with a method
    class TestClass2:
        def test_method(self) -> None:
            pass

    name = obj_qualname(TestClass2.test_method)
    assert name == "test_obj_qualname.<locals>.TestClass2.test_method", (
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


def test_unwrapped_obj() -> None:
    """Test function."""
    unwrapped_func = unwrapped_obj(_deeply_decorated_func)
    assert unwrapped_func.__name__ == "_deeply_decorated_func", (
        f"Expected '_deeply_decorated_func', got {unwrapped_func.__name__}"
    )

    unwrapped_method = unwrapped_obj(
        _TestDeeplyNestedClassMethod.deeply_nested_class_method
    )
    assert unwrapped_method.__name__ == "deeply_nested_class_method", (
        f"Expected 'deeply_nested_class_method', got {unwrapped_method.__name__}"
    )


def test_obj_module() -> None:
    """Test function."""

    # Test with a function
    def test_function() -> None:
        pass

    module = obj_module(test_function)
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

    method_module = obj_module(TestClass.test_method)
    assert method_module.__name__ == __name__, (
        f"Expected module name {__name__}, got {method_module.__name__}"
    )

    # Test with a property
    prop_module = obj_module(TestClass.test_property)
    assert prop_module.__name__ == __name__, (
        f"Expected module name {__name__}, got {prop_module.__name__}"
    )

    # Test with built-in function
    os_module = obj_module(os.path.join)
    assert "posixpath" in os_module.__name__ or "ntpath" in os_module.__name__, (
        f"Expected posixpath or ntpath module, got {os_module.__name__}"
    )

    # take an obj without a module and check if raises LookupError
    with pytest.raises(LookupError):
        obj_module("string without module")


def test_sorted_by_def_line() -> None:
    """Test function."""

    def test_func_a() -> None:
        pass

    def test_func_b() -> None:
        pass

    def test_func_c() -> None:
        pass

    funcs = [
        test_func_b,
        test_func_c,
        test_func_a,
        test_obj_module,
        test_obj_qualname,
        test_sorted_by_def_line,
    ]
    sorted_funcs = sorted(funcs, key=def_line)
    assert sorted_funcs == [
        test_obj_qualname,
        test_obj_module,
        test_sorted_by_def_line,
        test_func_a,
        test_func_b,
        test_func_c,
    ], "Expected functions sorted by definition line"
