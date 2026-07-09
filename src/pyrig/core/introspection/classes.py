"""Utilities for Python classes."""

import inspect
from collections.abc import Callable, Iterable, Iterator
from types import FunctionType, ModuleType
from typing import Any, cast

from pyrig_runtime.core.introspection.inspection import obj_members

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
    return (
        member
        for member in obj_members(unwrap_obj(cls))
        if inspect.isfunction(unwrap_obj(member))
    )


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
    for method in methods:
        unwrapped_method = unwrap_obj(method)
        unwrapped_cls = unwrap_obj(cls)
        if (
            inspect.getmodule(unwrapped_method) is inspect.getmodule(unwrapped_cls)
            and unwrapped_method.__name__ in unwrapped_cls.__dict__
        ):
            yield method


def filter_module_classes(
    module: ModuleType,
    members: Iterable[Any],
) -> Iterator[type]:
    """Filter an iterable of objects to keep only classes defined in a module.

    Args:
        module: Module to filter against.
        members: Iterable of objects to filter.

    Yields:
        Class types defined directly in `module`.
    """
    for member in members:
        unwrapped_member = unwrap_obj(member)
        if (
            inspect.isclass(unwrapped_member)
            and unwrapped_member.__module__ == module.__name__
        ):
            yield member


def generate_class[T](
    name: str,
    bases: tuple[type[T], ...],
    methods: tuple[FunctionType, ...],
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
        namespace[method.__name__] = method
    cls = type(name, bases, namespace)
    return cast("type[T]", cls)
