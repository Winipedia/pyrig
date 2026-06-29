"""Utilities for inspecting Python objects."""

import inspect
from collections.abc import Iterable
from typing import Any

from pyrig_runtime.core.introspection.inspection import unwrap_obj


def def_line_sorted(objs: Iterable[Any]) -> list[Any]:
    """Sort objects by their source definition line number.

    Args:
        objs: Iterable of objects to sort (functions, methods, properties, etc.).

    Returns:
        New list of objects sorted ascending by their definition line number.
    """
    return sorted(objs, key=def_line)


def def_line(obj: Any) -> int:
    """Return the 1-based source line where an object is defined.

    For properties, classmethods, staticmethods, and decorated callables, the
    underlying function's line is returned rather than the wrapper's line.

    Args:
        obj: Callable (function, method, property, staticmethod, classmethod,
            or decorated callable).

    Returns:
        1-based line number of the first line of the object's definition.

    Raises:
        OSError: If the source cannot be located, for example when the source
            file is missing or unavailable.
        TypeError: If the object is a built-in or C extension callable whose
            source cannot be retrieved.
    """
    unwrapped = unwrap_obj(obj)
    if hasattr(unwrapped, "__code__"):
        return int(unwrapped.__code__.co_firstlineno)
    return inspect.getsourcelines(unwrapped)[1]
