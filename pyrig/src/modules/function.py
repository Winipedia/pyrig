"""Function detection and extraction utilities.

Utilities for identifying callable objects and extracting functions from modules.
Handles functions, methods, staticmethods, classmethods, properties, and decorators.
"""

import inspect
from collections.abc import Callable
from importlib import import_module
from types import ModuleType
from typing import Any

from pyrig.src.modules.inspection import (
    get_def_line,
    get_module_of_obj,
    get_obj_members,
)


def is_func_or_method(obj: Any) -> bool:
    """Check if an object is a plain function or bound method.

    Args:
        obj: Object to check.

    Returns:
        True if function or method, False otherwise.

    Note:
        Does NOT detect staticmethod/classmethod/property. Use `is_func()` for those.
    """
    return inspect.isfunction(obj) or inspect.ismethod(obj)


def is_func(obj: Any) -> bool:
    """Check if an object is any kind of callable method-like attribute.

    Detects plain functions, staticmethod, classmethod, property, and decorators.

    Args:
        obj: Object to check.

    Returns:
        True if method-like callable, False otherwise.
    """
    if is_func_or_method(obj):
        return True

    if isinstance(obj, (staticmethod, classmethod, property)):
        return True

    unwrapped = inspect.unwrap(obj)

    return is_func_or_method(unwrapped)


def get_all_functions_from_module(
    module: ModuleType | str, *, include_annotate: bool = False
) -> list[Callable[..., Any]]:
    """Extract all functions defined directly in a module.

    Excludes imported functions. Returns functions sorted by definition order.

    Args:
        module: Module to extract from (object or name string).
        include_annotate: If False, excludes `__annotate__` (Python 3.14+).

    Returns:
        List of functions sorted by definition order.
    """
    if isinstance(module, str):
        module = import_module(module)
    funcs = [
        func
        for _name, func in get_obj_members(module, include_annotate=include_annotate)
        if is_func(func)
        if get_module_of_obj(func).__name__ == module.__name__
    ]
    # sort by definition order
    return sorted(funcs, key=get_def_line)


def unwrap_method(method: Any) -> Callable[..., Any] | Any:
    """Unwrap a method to its underlying function object.

    Handles staticmethod/classmethod, property, and decorators.

    Args:
        method: Method-like object to unwrap.

    Returns:
        Underlying unwrapped function.
    """
    if isinstance(method, (staticmethod, classmethod)):
        method = method.__func__
    if isinstance(method, property):
        method = method.fget
    return inspect.unwrap(method)


def is_abstractmethod(method: Any) -> bool:
    """Check if a method is marked as abstract.

    Args:
        method: Method to check (can be wrapped).

    Returns:
        True if method has `__isabstractmethod__` set to True.
    """
    method = unwrap_method(method)
    return getattr(method, "__isabstractmethod__", False)
