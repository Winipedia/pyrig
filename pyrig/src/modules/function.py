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
    def_line,
    module_of_obj,
    obj_members,
    unwrapped_obj,
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

    unwrapped = unwrapped_obj(obj)

    return is_func_or_method(unwrapped)


def all_functions_from_module(
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
        for _name, func in obj_members(module, include_annotate=include_annotate)
        if is_func(func)
        if module_of_obj(func).__name__ == module.__name__
    ]
    # sort by definition order
    return sorted(funcs, key=def_line)
