"""Utilities for introspecting and filtering Python classes."""

import inspect
from collections.abc import Callable, Iterable, Iterator
from types import ModuleType
from typing import Any

from pyrig_runtime.core.introspection.functions import is_funclike
from pyrig_runtime.core.introspection.inspection import obj_members, obj_module

from pyrig.core.introspection.inspection import unwrap_obj


def cls_methods(
    cls: type,
) -> Iterator[Callable[..., Any]]:
    """Extract all methods from a class, including inherited ones.

    Covers instance methods, static methods, class methods, and properties
    from the class itself and all ancestor classes. Results are yielded in
    alphabetical order by method name.

    To restrict results to methods defined directly on `cls`, pass the
    output to `discard_parent_methods`.

    Args:
        cls: Class to extract methods from.

    Yields:
        Method objects in alphabetical name order.
    """
    return (method for _name, method in obj_members(cls) if is_funclike(method))


def discard_parent_methods(
    cls: type,
    methods: Iterable[Callable[..., Any]],
) -> Iterator[Callable[..., Any]]:
    """Filter methods to keep only those defined directly on a class.

    A method is kept only when it is defined in the same module as `cls`
    and declared directly on `cls`, not inherited from a parent.

    Args:
        cls: The class whose own methods should be kept.
        methods: Iterable of method objects to filter.

    Yields:
        Methods that are defined directly on `cls`.
    """
    return (
        method
        for method in methods
        if obj_module(method) is obj_module(cls)
        and unwrap_obj(method).__name__ in cls.__dict__
    )


def module_classes(module: ModuleType) -> Iterator[type]:
    """Extract all classes defined directly in a module, excluding imported ones.

    Classes backed by C or Rust extensions (such as `cryptography`'s
    `AESGCM`) whose module origin cannot be resolved are silently excluded.

    Args:
        module: Module to inspect.

    Yields:
        Class types defined directly in `module`.
    """
    # necessary for bindings packages like AESGCM from cryptography._rust backend
    default = ModuleType(module_classes.__name__)  # to not match any real module
    return (
        obj
        for _, obj in obj_members(module, inspect.isclass)
        if obj_module(obj, default) is module
    )
