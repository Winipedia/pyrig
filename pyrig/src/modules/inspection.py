"""Low-level inspection utilities for Python object introspection.

This module provides foundational utilities for inspecting Python objects,
particularly focused on unwrapping decorated methods and accessing object
metadata. These utilities handle edge cases like properties, staticmethods,
classmethods, and decorator chains.

The module also provides detection for PyInstaller frozen bundles, where
some inspection operations behave differently or are unavailable.

Example:
    >>> from pyrig.src.modules.inspection import get_def_line, get_unwrapped_obj
    >>> class MyClass:
    ...     @property
    ...     def value(self):
    ...         return 42
    >>> get_def_line(MyClass.value)
    3
"""

import inspect
import sys
from collections.abc import Callable
from typing import Any, cast


def get_obj_members(
    obj: Any, *, include_annotate: bool = False
) -> list[tuple[str, Any]]:
    """Get all members of an object as name-value pairs.

    Retrieves all attributes of an object using `inspect.getmembers()`,
    optionally filtering out Python 3.14+ annotation-related methods
    that are typically not relevant for introspection.

    Args:
        obj: The object to inspect (typically a class or module).
        include_annotate: If False (default), excludes `__annotate__` and
            `__annotate_func__` methods introduced in Python 3.14. These
            are internal methods for deferred annotation evaluation.

    Returns:
        A list of (name, value) tuples for each member of the object.
    """
    members = [(member, value) for member, value in inspect.getmembers(obj)]
    if not include_annotate:
        members = [
            (member, value)
            for member, value in members
            if member not in ("__annotate__", "__annotate_func__")
        ]
    return members


def inside_frozen_bundle() -> bool:
    """Check if the code is running inside a PyInstaller frozen bundle.

    PyInstaller sets `sys.frozen` to True when running from a bundled
    executable. Some inspection operations (like `getsourcelines`) are
    unavailable in frozen bundles.

    Returns:
        True if running inside a frozen PyInstaller bundle, False otherwise.
    """
    return getattr(sys, "frozen", False)


def get_def_line(obj: Any) -> int:
    """Get the source line number where an object is defined.

    Handles various callable types including plain functions, methods,
    properties, staticmethods, classmethods, and decorated functions.
    Used for sorting functions/methods in definition order.

    Args:
        obj: A callable object (function, method, property, etc.).

    Returns:
        The 1-based line number where the object is defined in its source
        file. Returns 0 if running in a frozen bundle where source is
        unavailable.

    Note:
        For properties, returns the line where the getter is defined.
        Automatically unwraps decorator chains to find the original function.
    """
    if isinstance(obj, property):
        obj = obj.fget
    unwrapped = inspect.unwrap(obj)
    if hasattr(unwrapped, "__code__"):
        return int(unwrapped.__code__.co_firstlineno)
    # getsourcelines does not work if in a pyinstaller bundle or something
    if inside_frozen_bundle():
        return 0
    return inspect.getsourcelines(unwrapped)[1]


def get_unwrapped_obj(obj: Any) -> Any:
    """Unwrap a method-like object to its underlying function.

    Handles properties (extracts the getter), staticmethod/classmethod
    descriptors, and decorator chains. Useful for accessing the actual
    function object when you need to inspect its attributes.

    Args:
        obj: A callable object that may be wrapped (property, staticmethod,
            classmethod, or decorated function).

    Returns:
        The underlying unwrapped function object.

    Example:
        >>> class MyClass:
        ...     @staticmethod
        ...     def static_method():
        ...         pass
        >>> unwrapped = get_unwrapped_obj(MyClass.__dict__['static_method'])
        >>> unwrapped.__name__
        'static_method'
    """
    if isinstance(obj, property):
        obj = obj.fget  # get the getter function of the property
    return inspect.unwrap(obj)


def get_qualname_of_obj(obj: Callable[..., Any] | type) -> str:
    """Get the qualified name of a callable or type.

    The qualified name includes the class name for methods (e.g.,
    "MyClass.my_method") and handles wrapped/decorated objects.

    Args:
        obj: A callable (function, method) or type (class) to get the
            qualified name of.

    Returns:
        The qualified name string (e.g., "ClassName.method_name" for
        methods, "function_name" for module-level functions).

    Example:
        >>> class MyClass:
        ...     def my_method(self):
        ...         pass
        >>> get_qualname_of_obj(MyClass.my_method)
        'MyClass.my_method'
    """
    unwrapped = get_unwrapped_obj(obj)
    return cast("str", unwrapped.__qualname__)
