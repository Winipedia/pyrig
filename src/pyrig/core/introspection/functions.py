"""Utilities for detecting and extracting callable objects from modules."""

import inspect
from collections.abc import Callable, Iterator
from types import ModuleType
from typing import Any

from pyrig.core.introspection.inspection import (
    obj_members,
    obj_module,
    unwrapped_obj,
)


def module_functions(
    module: ModuleType,
) -> Iterator[Callable[..., Any]]:
    """Yield all funclike objects defined directly in a module, excluding imports.

    A funclike object is included only when its defining module matches
    `module`, which filters out any names that were imported from other modules.
    See [is_funclike][] for what counts as funclike.

    Args:
        module: Module to extract funclike objects from.

    Yields:
        Each funclike object defined in `module`, in member-name order.
    """
    return (
        func
        for _name, func in obj_members(module)
        if is_funclike(func)
        if obj_module(func) is module
    )


def is_funclike(obj: Any) -> bool:
    """Return `True` if an object is a function or any method-like descriptor.

    Covers all forms that may appear as a method or function in a class or
    module namespace:

    - Plain functions and bound methods
    - `staticmethod` and `classmethod` descriptors
    - `property` descriptors (and custom descriptor subclasses)
    - Functions wrapped with `functools.wraps` or similar decorators

    Args:
        obj: Object to test.

    Returns:
        `True` if the object is a function or any method-like descriptor,
        `False` otherwise.
    """
    return is_func_or_method(unwrapped_obj(obj))


def is_func_or_method(obj: Any) -> bool:
    """Return `True` if an object is a plain function or a bound method.

    Does not detect `staticmethod`, `classmethod`, or `property` descriptors
    when accessed through a class `__dict__`; use [is_funclike][] for those.

    Args:
        obj: Object to test.

    Returns:
        `True` if `obj` is a plain function or a bound method, `False`
        otherwise.
    """
    return inspect.isfunction(obj) or inspect.ismethod(obj)
