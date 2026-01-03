"""Low-level inspection utilities for Python object introspection.

Utilities for inspecting Python objects, unwrapping decorated methods, and accessing
object metadata. Handles properties, staticmethods, classmethods, and decorator chains.
"""

import inspect
import sys
from collections.abc import Callable
from types import ModuleType
from typing import Any, cast


def get_obj_members(
    obj: Any, *, include_annotate: bool = False
) -> list[tuple[str, Any]]:
    """Get all members of an object as name-value pairs.

    Args:
        obj: Object to inspect (class or module).
        include_annotate: If False, excludes `__annotate__` (Python 3.14+).

    Returns:
        List of (name, value) tuples.
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

    Handles functions, methods, properties, staticmethods, classmethods, and decorators.

    Args:
        obj: Callable object.

    Returns:
        1-based line number (0 if in frozen bundle).
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

    Handles properties, staticmethod/classmethod descriptors, and decorators.

    Args:
        obj: Callable that may be wrapped.

    Returns:
        Underlying unwrapped function.
    """
    if hasattr(obj, "__func__"):
        obj = obj.__func__
    if hasattr(obj, "fget"):
        obj = obj.fget
    return inspect.unwrap(obj)


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

    Args:
        obj: Method-like object (function, method, property, staticmethod, classmethod).
        default: Default module if module cannot be determined.

    Returns:
        Module object.

    Raises:
        ValueError: If module cannot be determined and no default provided.
    """
    unwrapped = get_unwrapped_obj(obj)
    module = inspect.getmodule(unwrapped)
    if not module:
        msg = f"Could not determine module of {obj}"
        if default:
            return default
        raise ValueError(msg)
    return module
