"""Utilities for inspecting Python objects."""

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
        objs: Modules, classes, functions or methods, tracebacks, frames, or
            code objects to sort.

    Returns:
        New list of objects sorted ascending by their definition line number.

    Raises:
        OSError: If the source cannot be located for any of the objects.
        TypeError: If any of the objects is a built-in or C extension
            module, class, or callable whose source cannot be retrieved.
    """
    return sorted(objs, key=def_line)


def def_line(
    obj: SourceObjectType,
) -> int:
    """Return the 1-based source line where an object is defined.

    Accepts a module, class, function, method, traceback, frame, or code
    object. Properties, classmethods, staticmethods, and other decorated
    callables are unwrapped first, so the underlying function's line is
    returned rather than the wrapper's line.

    Args:
        obj: Object whose definition line to locate.

    Returns:
        1-based line number of the first line of the object's definition.

    Raises:
        OSError: If the source cannot be located, for example when the source
            file is missing or unavailable.
        TypeError: If the object is a built-in or C extension module, class,
            or callable whose source cannot be retrieved.
    """
    unwrapped = unwrap_obj(obj)
    code = getattr(unwrapped, "__code__", None)
    if code is not None:
        return code.co_firstlineno
    return inspect.findsource(unwrapped)[1] + 1
