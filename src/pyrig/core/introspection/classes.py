"""Class introspection and subclass discovery utilities.

Utilities for inspecting classes, extracting methods, and discovering subclasses across
packages. Central to pyrig's plugin architecture for automatic discovery of ConfigFile
implementations and BuilderConfigFile subclasses.
"""

import inspect
from collections.abc import Callable, Generator, Iterable
from types import ModuleType
from typing import Any

from pyrig.core.introspection.functions import is_func
from pyrig.core.introspection.inspection import (
    module_of_obj,
    obj_members,
    unwrapped_obj,
)


def all_methods_from_cls(
    cls: type,
) -> Generator[Callable[..., Any], None, None]:
    """Extract all methods from a class.

    Includes instance methods, static methods, class methods, and properties.
    Returns methods sorted by definition order.

    Args:
        cls: Class to extract methods from.

    Returns:
        Generator of method objects sorted by definition order.
    """
    return (method for _name, method in obj_members(cls) if is_func(method))


def discard_parent_methods(
    cls: type,
    methods: Iterable[Callable[..., Any]],
) -> Generator[Callable[..., Any], None, None]:
    """Keeps only methods defined in that actual class, discarding inherited methods."""
    return (
        method
        for method in methods
        if module_of_obj(method).__name__ == cls.__module__
        and unwrapped_obj(method).__name__ in cls.__dict__
    )


def all_cls_from_module(module: ModuleType) -> Generator[type]:
    """Extract all classes defined directly in a module.

    Args:
        module: Module object or fully qualified module name.

    Returns:
        Generator of class types sorted by definition order.

    Note:
        Handles edge cases like Rust-backed classes (e.g., cryptography's AESGCM).
    """
    # necessary for bindings packages like AESGCM from cryptography._rust backend
    default = ModuleType(all_cls_from_module.__name__)  # to not match any real module
    return (
        obj
        for _, obj in obj_members(module, inspect.isclass)
        if module_of_obj(obj, default).__name__ == module.__name__
    )


def discover_all_subclasses[T: type](cls: T) -> set[T]:
    """Discover all subclasses of a class without loading any packages.

    Uses only the existing class registry (``__subclasses__()``) without
    importing any new modules. This is useful when you want to discover
    subclasses that are already loaded, without triggering imports.

    Args:
        cls: Base class to find subclasses of. The base class itself is
            included in the results.

    Returns:
        Set of discovered subclass types (including ``cls`` itself).
    """
    subclasses = {cls, *cls.__subclasses__()}
    for subclass in cls.__subclasses__():
        subclasses.update(discover_all_subclasses(subclass))
    return subclasses


def discard_parent_classes[T: type](
    classes: Iterable[T],
) -> Generator[T, None, None]:
    """Remove parent classes when their children are also present.

    Keeps only "leaf" classes - those with no subclasses in the collection.
    Enables clean override behavior where derived classes override base implementations.

    Args:
        classes: List or set of class types to filter. The collection is modified
            in place (elements are removed from the original collection) by iterating
            over a copy and removing parent classes from the original.

    Returns:
        The same collection instance with parent classes removed.
    """
    classes = set(classes)  # ensure we have a set for O(1) lookups
    return (
        cls
        for cls in classes
        if not any(
            candidate is not cls and issubclass(candidate, cls) for candidate in classes
        )
    )


def discard_abstract_classes[T: type](classes: Iterable[T]) -> Generator[T, None, None]:
    """Remove abstract classes from a collection.

    Args:
        classes: Iterable of class types to filter.

    Yields:
        Non-abstract classes from the input collection.
    """
    return (cls for cls in classes if not inspect.isabstract(cls))


class classproperty[T]:  # noqa: N801
    """Decorator that creates a property accessible on the class itself.

    Unlike @property which only works on instances, @classproperty allows
    accessing the property directly on the class. Can be combined with
    caching by using @cache on the underlying method.

    Example:
        >>> class MyClass:
        ...     @classproperty
        ...     def cls_name(cls) -> str:
        ...         return cls.__name__.lower()
        ...
        >>> MyClass.cls_name # returns 'myclass'
        'myclass'

    Args:
        fget: The method to wrap as a class property.
    """

    __slots__ = ("fget",)

    def __init__(self, fget: Callable[..., T]) -> None:
        """Initialize with the getter method."""
        self.fget = fget

    def __get__(self, obj: object, owner: type) -> T:
        """Return the property value by invoking the getter with the owner class."""
        return self.fget(owner)
