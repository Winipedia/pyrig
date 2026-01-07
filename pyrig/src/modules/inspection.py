"""Low-level inspection utilities for Python object introspection.

Provides foundational utilities for inspecting Python objects, unwrapping decorated
methods, and accessing object metadata. Handles properties, staticmethods, classmethods,
and decorator chains. Used by higher-level modules (`class_`, `function`, `module`)
for method extraction, subclass discovery, and test generation throughout pyrig.
"""

import inspect
import sys
from collections.abc import Callable
from types import ModuleType
from typing import Any, cast


def get_obj_members(
    obj: Any, *, include_annotate: bool = False
) -> list[tuple[str, Any]]:
    """Get all members of an object as name-value pairs using static introspection.

    Uses `inspect.getmembers_static` to retrieve members without invoking descriptors,
    making it safe for introspecting classes with properties that have side effects.

    Args:
        obj: Object to inspect (class, module, or any Python object).
        include_annotate: If False, excludes `__annotate__` and `__annotate_func__`
            attributes added in Python 3.14+ for deferred annotation evaluation.

    Returns:
        List of (name, value) tuples for all object members.
    """
    members = [(member, value) for member, value in inspect.getmembers_static(obj)]
    if not include_annotate:
        members = [
            (member, value)
            for member, value in members
            if member not in ("__annotate__", "__annotate_func__")
        ]
    return members


def inside_frozen_bundle() -> bool:
    """Check if running inside a PyInstaller frozen bundle.

    Returns:
        True if in frozen bundle, False otherwise.
    """
    return getattr(sys, "frozen", False)


def get_def_line(obj: Any) -> int:
    """Get the source line number where an object is defined.

    Handles functions, methods, properties, staticmethods, classmethods, and decorators
    by first unwrapping to the underlying function. Used for sorting functions and
    methods by their definition order in source code.

    Args:
        obj: Callable object (function, method, property, staticmethod, classmethod,
            or decorated callable).

    Returns:
        1-based source line number. Returns 0 if running inside a PyInstaller frozen
        bundle where source introspection is unavailable.
    """
    if isinstance(obj, property):
        obj = obj.fget
    unwrapped = get_unwrapped_obj(obj)
    if hasattr(unwrapped, "__code__"):
        return int(unwrapped.__code__.co_firstlineno)
    # getsourcelines does not work if in a pyinstaller bundle or something
    if inside_frozen_bundle():
        return 0
    return inspect.getsourcelines(unwrapped)[1]


def get_unwrapped_obj(obj: Any) -> Any:
    """Unwrap a method-like object to its underlying function.

    Iteratively unwraps layers of wrapping until reaching the original function:
        1. Extracts `__func__` from bound methods and classmethod/staticmethod
        2. Extracts `fget` from property objects
        3. Uses `inspect.unwrap` to traverse `functools.wraps` decorator chains

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


def get_qualname_of_obj(obj: Callable[..., Any] | type) -> str:
    """Get the qualified name of a callable or type.

    Includes class name for methods (e.g., "MyClass.my_method").

    Args:
        obj: Callable or type.

    Returns:
        Qualified name string.
    """
    unwrapped = get_unwrapped_obj(obj)
    return cast("str", unwrapped.__qualname__)


def get_module_of_obj(obj: Any, default: ModuleType | None = None) -> ModuleType:
    """Return the module where a method-like object is defined.

    Unwraps the object first to handle decorated functions, then uses
    `inspect.getmodule` to determine the defining module. Essential for filtering
    functions/classes to only those defined directly in a module (excluding imports).

    Args:
        obj: Method-like object (function, method, property, staticmethod, classmethod,
            or decorated callable).
        default: Fallback module to return if the module cannot be determined.

    Returns:
        The module object where the callable is defined.

    Raises:
        ValueError: If module cannot be determined and no default is provided.
    """
    unwrapped = get_unwrapped_obj(obj)
    module = inspect.getmodule(unwrapped)
    if not module:
        msg = f"Could not determine module of {obj}"
        if default:
            return default
        raise ValueError(msg)
    return module
