"""Low-level inspection utilities for Python object introspection.

Provides foundational utilities for inspecting Python objects, unwrapping decorated
methods, and accessing object metadata. Handles properties, staticmethods, classmethods,
and decorator chains.
Used by higher-level modules (``class_``, ``function``, ``module``)
for method extraction, subclass discovery, and test generation throughout pyrig.
"""

import inspect
from collections.abc import Callable, Generator, Iterable
from types import ModuleType
from typing import Any, cast


def obj_members(
    obj: Any, predicate: Callable[[Any], bool] | None = None
) -> Generator[tuple[str, Any], None, None]:
    """Get all members of an object as name-value pairs using static introspection.

    Uses ``inspect.getmembers_static`` to retrieve members without invoking descriptors,
    making it safe for introspecting classes with properties that have side effects.

    Args:
        obj: Object to inspect (class, module, or any Python object).
        predicate: Optional predicate function to filter members.

    Returns:
        Generator of (name, value) tuples for all object members.
    """
    return (
        (member, value)
        for member, value in inspect.getmembers_static(obj, predicate=predicate)
        if member not in ("__annotate__", "__annotate_func__")
    )


def def_line(obj: Any) -> int:
    """Get the source line number where an object is defined.

    Handles functions, methods, properties, staticmethods, classmethods, and decorators
    by first unwrapping to the underlying function. Used for sorting functions and
    methods by their definition order in source code.

    Args:
        obj: Callable object (function, method, property, staticmethod, classmethod,
            or decorated callable).

    Returns:
        1-based source line number. Returns 0 only if the object has no
        ``__code__`` attribute and is running inside a PyInstaller frozen
        bundle where source introspection is unavailable.
    """
    if isinstance(obj, property):
        obj = obj.fget
    unwrapped = unwrapped_obj(obj)
    if hasattr(unwrapped, "__code__"):
        return int(unwrapped.__code__.co_firstlineno)

    return inspect.getsourcelines(unwrapped)[1]


def sorted_by_def_line(objs: Iterable[Any]) -> list[Any]:
    """Sort a list of objects by their source definition line number.

    Uses ``def_line`` to determine the line number for each object, allowing for
    sorting functions, methods, properties, staticmethods, classmethods, and decorated
    callables in the order they are defined in source code.

    Args:
        objs: List of objects to sort (functions, methods, properties, etc.).

    Returns:
        New list of objects sorted by their definition line number.
    """
    return sorted(objs, key=def_line)


def unwrapped_obj(obj: Any) -> Any:
    """Unwrap a method-like object to its underlying function.

    Iteratively unwraps layers of wrapping until reaching the original function:
        1. Extracts ``__func__`` from bound methods and classmethod/staticmethod
        2. Extracts ``fget`` from property objects
        3. Uses ``inspect.unwrap`` to traverse ``functools.wraps`` decorator chains

    Continues until no further unwrapping is possible.

    Args:
        obj: Callable that may be wrapped (method, property, staticmethod, classmethod,
            or decorated function).

    Returns:
        The underlying unwrapped function object.
    """
    prev = None
    while prev is not obj:
        prev = obj
        if hasattr(obj, "__func__"):
            obj = obj.__func__
        if hasattr(obj, "fget"):
            obj = obj.fget
        obj = inspect.unwrap(obj)
    return obj


def obj_qualname(obj: Callable[..., Any] | type) -> str:
    """Get the qualified name of a callable or type.

    Includes class name for methods (e.g., "MyClass.my_method").

    Args:
        obj: Callable or type.

    Returns:
        Qualified name string.
    """
    unwrapped = unwrapped_obj(obj)
    return cast("str", unwrapped.__qualname__)


def obj_module(obj: Any, default: ModuleType | None = None) -> ModuleType:
    """Return the module where a method-like object is defined.

    Unwraps the object first to handle decorated functions, then uses
    ``inspect.getmodule`` to determine the defining module. Essential for filtering
    functions/classes to only those defined directly in a module (excluding imports).

    Args:
        obj: Method-like object (function, method, property, staticmethod, classmethod,
            or decorated callable).
        default: Fallback module to return if the module cannot be determined.

    Returns:
        The module object where the callable is defined.

    Raises:
        LookupError: If module cannot be determined and no default is provided.
    """
    unwrapped = unwrapped_obj(obj)
    module = inspect.getmodule(unwrapped)
    if not module:
        msg = f"Could not determine module of {obj}"
        if default:
            return default
        raise LookupError(msg)
    return module
