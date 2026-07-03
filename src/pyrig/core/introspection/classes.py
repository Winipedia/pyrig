"""Utilities for introspecting and filtering Python classes."""

import inspect
from collections.abc import Callable, Iterable, Iterator
from types import ModuleType
from typing import Any, cast

from pyrig_runtime.core.introspection.functions import is_funclike
from pyrig_runtime.core.introspection.inspection import obj_members, obj_module

from pyrig.core.introspection.inspection import unwrap_obj


def cls_methods(
    cls: type,
) -> Iterator[Callable[..., Any]]:
    """Extract all methods and properties from a class, including inherited ones.

    Args:
        cls: Class to extract methods from.

    Yields:
        Instance methods, static methods, class methods, and properties,
        in alphabetical order by name.
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


def generate_class[T](
    name: str,
    bases: tuple[type[T], ...],
    methods: tuple[Callable[..., Any], ...],
    namespace: dict[str, Any] | None = None,
) -> type[T]:
    """Dynamically create a class from base classes, methods, and attributes.

    Args:
        name: Name of the new class, used as its `__name__`.
        bases: Base classes the new class inherits from.
        methods: Functions to add to the class, each under its own `__name__`.
        namespace: Extra attributes for the class body, keyed by name. The
            `methods` are added on top, so a method whose name matches a key
            here overrides it. Defaults to an empty namespace.

    Returns:
        The newly created class.
    """
    if namespace is None:
        namespace = {}
    for method in methods:
        namespace[method.__name__] = method  # ty:ignore[unresolved-attribute]
    cls = type(name, bases, namespace)
    return cast("type[T]", cls)
