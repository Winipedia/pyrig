"""Function detection and extraction utilities.

This module provides utilities for identifying callable objects and extracting
functions from modules. It handles the various forms that "functions" can take
in Python, including plain functions, methods, staticmethods, classmethods,
properties, and decorated functions.

These utilities are used by pyrig to discover CLI subcommands from modules
and to extract testable functions for automatic test skeleton generation.

Example:
    >>> from pyrig.src.modules.function import get_all_functions_from_module
    >>> import my_module
    >>> functions = get_all_functions_from_module(my_module)
    >>> [f.__name__ for f in functions]
    ['func_a', 'func_b', 'func_c']
"""

import inspect
from collections.abc import Callable
from importlib import import_module
from types import ModuleType
from typing import Any

from pyrig.src.modules.inspection import get_def_line, get_obj_members


def is_func_or_method(obj: Any) -> bool:
    """Check if an object is a plain function or bound method.

    This is a basic check using `inspect.isfunction` and `inspect.ismethod`.
    For a more comprehensive check that includes staticmethods, classmethods,
    and properties, use `is_func()` instead.

    Args:
        obj: The object to check.

    Returns:
        True if the object is a function or bound method, False otherwise.

    Note:
        This does NOT detect staticmethod/classmethod descriptors or properties.
        Use `is_func()` for those cases.
    """
    return inspect.isfunction(obj) or inspect.ismethod(obj)


def is_func(obj: Any) -> bool:
    """Check if an object is any kind of callable method-like attribute.

    Provides comprehensive detection of callable objects as they appear in
    class bodies or modules. This includes:
        - Plain functions (which become instance methods in classes)
        - staticmethod descriptors
        - classmethod descriptors
        - property descriptors (the getter is considered a method)
        - Decorated functions with a `__wrapped__` chain

    Args:
        obj: The object to check.

    Returns:
        True if the object is a method-like callable, False otherwise.

    Example:
        >>> class MyClass:
        ...     def method(self): pass
        ...     @staticmethod
        ...     def static(): pass
        ...     @property
        ...     def prop(self): return 1
        >>> is_func(MyClass.method)
        True
        >>> is_func(MyClass.__dict__['static'])
        True
        >>> is_func(MyClass.prop)
        True
    """
    if is_func_or_method(obj):
        return True

    if isinstance(obj, (staticmethod, classmethod, property)):
        return True

    unwrapped = inspect.unwrap(obj)

    return is_func_or_method(unwrapped)


def get_all_functions_from_module(
    module: ModuleType | str, *, include_annotate: bool = False
) -> list[Callable[..., Any]]:
    """Extract all functions defined directly in a module.

    Retrieves all function objects that are defined in the specified module,
    excluding functions imported from other modules. Functions are returned
    sorted by their definition order (line number in source).

    This is used by pyrig to discover CLI subcommands and to generate test
    skeletons for module-level functions.

    Args:
        module: The module to extract functions from. Can be a module object
            or a module name string.
        include_annotate: If False (default), excludes `__annotate__` methods
            introduced in Python 3.14. These are internal and not user-defined.

    Returns:
        A list of callable functions defined in the module, sorted by their
        definition order in the source file.

    Example:
        >>> import my_module
        >>> funcs = get_all_functions_from_module(my_module)
        >>> [f.__name__ for f in funcs]
        ['first_function', 'second_function', 'third_function']
    """
    from pyrig.src.modules.module import (  # noqa: PLC0415  # avoid circular import
        get_module_of_obj,
    )

    if isinstance(module, str):
        module = import_module(module)
    funcs = [
        func
        for _name, func in get_obj_members(module, include_annotate=include_annotate)
        if is_func(func)
        if get_module_of_obj(func).__name__ == module.__name__
    ]
    # sort by definition order
    return sorted(funcs, key=get_def_line)


def unwrap_method(method: Any) -> Callable[..., Any] | Any:
    """Unwrap a method to its underlying function object.

    Handles staticmethod/classmethod descriptors (extracts `__func__`),
    properties (extracts the getter), and decorated functions (follows
    the `__wrapped__` chain).

    Args:
        method: The method-like object to unwrap. Can be a function,
            staticmethod, classmethod, property, or decorated callable.

    Returns:
        The underlying unwrapped function object.

    Example:
        >>> class MyClass:
        ...     @staticmethod
        ...     def static_method():
        ...         pass
        >>> raw_descriptor = MyClass.__dict__['static_method']
        >>> unwrap_method(raw_descriptor).__name__
        'static_method'
    """
    if isinstance(method, (staticmethod, classmethod)):
        method = method.__func__
    if isinstance(method, property):
        method = method.fget
    return inspect.unwrap(method)


def is_abstractmethod(method: Any) -> bool:
    """Check if a method is marked as abstract.

    Detects methods decorated with `@abstractmethod` (or variants like
    `@abstractclassmethod`, `@abstractproperty`). Handles wrapped methods
    by unwrapping them first.

    Args:
        method: The method to check. Can be wrapped in staticmethod,
            classmethod, property, or decorators.

    Returns:
        True if the method has `__isabstractmethod__` set to True,
        False otherwise.

    Example:
        >>> from abc import ABC, abstractmethod
        >>> class MyABC(ABC):
        ...     @abstractmethod
        ...     def must_implement(self):
        ...         pass
        >>> is_abstractmethod(MyABC.must_implement)
        True
    """
    method = unwrap_method(method)
    return getattr(method, "__isabstractmethod__", False)
