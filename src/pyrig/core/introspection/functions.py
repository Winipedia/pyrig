"""Function detection and extraction utilities.

Utilities for identifying callable objects and extracting functions from modules.
Handles functions, methods, staticmethods, classmethods, properties, and decorators.
"""

import inspect
from collections.abc import Callable, Generator
from types import ModuleType
from typing import Any

from pyrig.core.introspection.inspection import (
    obj_members,
    obj_module,
    unwrapped_obj,
)


def is_func_or_method(obj: Any) -> bool:
    """Check if an object is a plain function or bound method.

    Args:
        obj: Object to check.

    Returns:
        True if function or method, False otherwise.

    Note:
        Does NOT detect staticmethod/classmethod/property.
        Use `is_funclike()` for those.
    """
    return inspect.isfunction(obj) or inspect.ismethod(obj)


def is_funclike(obj: Any) -> bool:
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
    module: ModuleType,
) -> Generator[Callable[..., Any], None, None]:
    """Extract all functions defined directly in a module.

    Excludes imported functions.

    Args:
        module: Module to extract from (object or name string).

    Returns:
        Generator of functions
    """
    return (
        func
        for _name, func in obj_members(module)
        if is_funclike(func)
        if obj_module(func).__name__ == module.__name__
    )
