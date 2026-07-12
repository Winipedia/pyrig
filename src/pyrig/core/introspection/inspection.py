"""Utilities for locating an object's source definition line."""

import inspect
from collections.abc import Iterable

from pyrig_runtime.core.introspection.inspection import unwrap_obj


def def_line_sorted[T: object](objs: Iterable[T]) -> list[T]:
    """Sort objects by their source definition line number.

    Args:
        objs: Iterable of objects to sort (functions, methods, classes, etc.).

    Returns:
        New list of objects sorted ascending by their definition line number.
    """
    return sorted(objs, key=def_line)


def def_line(obj: object) -> int:
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
