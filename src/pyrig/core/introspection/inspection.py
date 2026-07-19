"""Utilities for locating an object's source definition line."""

import inspect
from collections.abc import Callable, Iterable
from types import (
    CodeType,
    FrameType,
    FunctionType,
    ModuleType,
    TracebackType,
)
from typing import Any, cast

from pyrig_runtime.core.introspection.inspection import unwrap_obj

type SourceObjectType = (
    ModuleType | type[Any] | Callable[..., Any] | TracebackType | FrameType | CodeType
)


def unwrap_cls(
    cls: Callable[..., Any],
) -> type:
    """Unwrap a class to its original implementation.

    Args:
        cls: Class to unwrap.

    Returns:
        The original class, unwrapped from any decorators or wrappers.
    """
    return cast("type", unwrap_obj(cls))


def unwrap_func(
    func: Callable[..., Any],
) -> FunctionType:
    """Unwrap a function to its original implementation.

    Args:
        func: Function to unwrap.

    Returns:
        The original function, unwrapped from any decorators or wrappers.
    """
    return cast("FunctionType", unwrap_obj(func))


def def_line_sorted[
    T: SourceObjectType,
](
    objs: Iterable[T],
) -> list[T]:
    """Sort objects by their source definition line number.

    Args:
        objs: Iterable of objects to sort (functions, methods, classes, etc.).

    Returns:
        New list of objects sorted ascending by their definition line number.
    """
    return sorted(objs, key=def_line)


def def_line(
    obj: SourceObjectType,
) -> int:
    """Return the 1-based source line where an object is defined.

    For properties, classmethods, staticmethods, and decorated callables, the
    underlying function's line is returned rather than the wrapper's line.

    Args:
        obj: Function, method, class, property, staticmethod, classmethod, or
            decorated callable.

    Returns:
        1-based line number of the first line of the object's definition.

    Raises:
        OSError: If the source cannot be located, for example when the source
            file is missing or unavailable.
        TypeError: If the object is a built-in or C extension callable whose
            source cannot be retrieved.
    """
    unwrapped = unwrap_obj(obj)
    code = getattr(unwrapped, "__code__", None)
    if code is not None:
        return code.co_firstlineno
    return inspect.findsource(unwrapped)[1] + 1
