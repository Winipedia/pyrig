"""Utilities for detecting and extracting callable objects from modules."""

import inspect
from collections.abc import Callable, Generator
from types import ModuleType
from typing import Any

from pyrig.core.introspection.inspection import (
    obj_members,
    obj_module,
    unwrapped_obj,
)


def all_functions_from_module(
    module: ModuleType,
) -> Generator[Callable[..., Any], None, None]:
    """Yield all functions defined directly in a module, excluding imports.

    A function is included only when its ``__module__`` attribute matches the
    module being inspected, which filters out any names that were imported from
    other modules. All callable forms are covered: plain functions, staticmethods,
    classmethods, properties, and decorated callables.

    Args:
        module: The module object to extract functions from.

    Yields:
        Each function defined in ``module`` in the order returned by
        ``inspect.getmembers_static``.
    """
    return (
        func
        for _name, func in obj_members(module)
        if is_funclike(func)
        if obj_module(func).__name__ == module.__name__
    )


def is_funclike(obj: Any) -> bool:
    """Return True if an object is any callable method-like attribute.

    Covers all forms that may appear as a method or function in a class or
    module namespace:

    - Plain functions and bound/unbound methods (via ``is_func_or_method``)
    - ``staticmethod`` and ``classmethod`` descriptors
    - ``property`` descriptors (and custom descriptor subclasses)
    - Functions wrapped with ``functools.wraps`` or similar decorators

    The check works by unwrapping the object to its original
    function (if it is a decorated callable) and then checking if that
    unwrapped object is a plain function or method.

    Args:
        obj: The object to test.

    Returns:
        True if the object is a function or any method-like descriptor,
        False otherwise.
    """
    return is_func_or_method(unwrapped_obj(obj))


def is_func_or_method(obj: Any) -> bool:
    """Return True if an object is a plain function or a bound/unbound method.

    Uses ``inspect.isfunction`` and ``inspect.ismethod`` directly. This does
    not detect ``staticmethod``, ``classmethod``, or ``property`` descriptors
    when accessed through a class ``__dict__``; use ``is_funclike`` for those.

    Args:
        obj: The object to test.

    Returns:
        True if ``obj`` is a plain function or a bound/unbound method,
        False otherwise.
    """
    return inspect.isfunction(obj) or inspect.ismethod(obj)
