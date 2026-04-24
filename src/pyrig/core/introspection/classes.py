"""Utilities for classes.

This module provides functionality to introspect classes,
discover their methods, filter out inherited methods,
and identify classes defined in a module.
It also includes a custom descriptor for class-level properties.
"""

import inspect
from collections.abc import Callable, Generator, Iterable
from types import ModuleType
from typing import Any

from pyrig.core.introspection.functions import is_funclike
from pyrig.core.introspection.inspection import (
    obj_members,
    obj_module,
    unwrapped_obj,
)


def cls_methods(
    cls: type,
) -> Generator[Callable[..., Any], None, None]:
    """Extract all methods from a class.

    Includes instance methods, static methods, class methods, and properties.
    Results are yielded in alphabetical order by method name, as determined by
    the underlying ``inspect.getmembers_static`` call.

    Args:
        cls: Class to extract methods from.

    Returns:
        Generator of method objects in alphabetical name order.
    """
    return (method for _name, method in obj_members(cls) if is_funclike(method))


def discard_parent_methods(
    cls: type,
    methods: Iterable[Callable[..., Any]],
) -> Generator[Callable[..., Any], None, None]:
    """Filter methods to exclude inherited ones.

    This leaves only methods that are defined directly on the given class,
    excluding any methods that are inherited from parent classes.
    A method passes the filter only when both of the following hold:

    - Its defining module matches the module where ``cls`` is defined.
    - Its unwrapped name is present in ``cls.__dict__``, confirming it was
      declared on ``cls`` itself rather than inherited from a parent class.

    Args:
        cls: The class whose own methods should be kept.
        methods: Iterable of method objects to filter.

    Yields:
        Methods that are defined directly on ``cls``.
    """
    return (
        method
        for method in methods
        if obj_module(method).__name__ == cls.__module__
        and unwrapped_obj(method).__name__ in cls.__dict__
    )


def module_classes(module: ModuleType) -> Generator[type]:
    """Extract all classes defined directly in a module, excluding imported ones.

    A sentinel ``ModuleType`` instance named after this function is used as the
    fallback when ``obj_module`` cannot resolve a class's origin (for example,
    classes backed by C or Rust extensions such as ``cryptography``'s ``AESGCM``).
    Because no real module shares that sentinel name, those classes are safely
    excluded rather than raising an error.

    Args:
        module: Module to inspect.

    Returns:
        Generator of class types that are defined in ``module``.
    """
    # necessary for bindings packages like AESGCM from cryptography._rust backend
    default = ModuleType(module_classes.__name__)  # to not match any real module
    return (
        obj
        for _, obj in obj_members(module, inspect.isclass)
        if obj_module(obj, default).__name__ == module.__name__
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
    """Yield only leaf classes, removing any ancestors present in the collection.

    A class is kept only when no other class in the collection is a strict subclass
    of it. This effectively yields "leaf" classes — those with no descendants
    in the collection — and is useful when derived classes should take precedence
    over their base classes.

    The input iterable is converted to a set internally; the original object is
    not modified.

    Args:
        classes: Iterable of class types to filter.

    Yields:
        Classes that have no subclasses present in the same collection.
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
    """Filter out abstract classes from a collection.

    Uses ``inspect.isabstract`` to detect classes that still have unimplemented
    abstract methods (i.e., classes with ``ABCMeta`` that cannot be instantiated).

    Args:
        classes: Iterable of class types to filter.

    Yields:
        Concrete (non-abstract) classes from the input.
    """
    return (cls for cls in classes if not inspect.isabstract(cls))


class classproperty[T]:  # noqa: N801
    """Descriptor that exposes a property computed from the class, not an instance.

    Unlike ``@property``, which requires an instance, ``@classproperty`` can be
    accessed directly on the class. Because ``__get__`` always receives the owner
    class as ``owner``, it also works correctly when accessed from an instance.

    Combine with ``@functools.cache`` on the underlying method to cache the
    computed value per class.

    Example:
        >>> class MyClass:
        ...     @classproperty
        ...     def cls_name(cls) -> str:
        ...         return cls.__name__.lower()
        ...
        >>> MyClass.cls_name
        'myclass'

    Args:
        fget: The callable to invoke with the owner class when the property is accessed.
    """

    __slots__ = ("fget",)

    def __init__(self, fget: Callable[..., T]) -> None:
        """Store the getter callable."""
        self.fget = fget

    def __get__(self, obj: object, owner: type) -> T:
        """Invoke the getter with the owner class and return the result."""
        return self.fget(owner)
