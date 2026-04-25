"""Utilities for introspecting and filtering Python classes."""

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
    """Extract all methods from a class, including inherited ones.

    Covers instance methods, static methods, class methods, and properties
    from the class itself and all ancestor classes. Results are yielded in
    alphabetical order by method name, as determined by
    ``inspect.getmembers_static``.

    To restrict results to methods defined directly on ``cls``, pass the
    output to ``discard_parent_methods``.

    Args:
        cls: Class to extract methods from.

    Yields:
        Method objects in alphabetical name order.
    """
    return (method for _name, method in obj_members(cls) if is_funclike(method))


def discard_parent_methods(
    cls: type,
    methods: Iterable[Callable[..., Any]],
) -> Generator[Callable[..., Any], None, None]:
    """Filter methods to keep only those defined directly on a class.

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

    Yields:
        Class types defined directly in ``module``.
    """
    # necessary for bindings packages like AESGCM from cryptography._rust backend
    default = ModuleType(module_classes.__name__)  # to not match any real module
    return (
        obj
        for _, obj in obj_members(module, inspect.isclass)
        if obj_module(obj, default).__name__ == module.__name__
    )


def discover_all_subclasses[T: type](cls: T) -> set[T]:
    """Recursively discover all subclasses of a class already loaded in memory.

    Traverses the live subclass registry via ``__subclasses__()`` without
    triggering any imports. Only subclasses whose modules are already loaded
    will appear in the result.

    Args:
        cls: Base class to find subclasses of.

    Returns:
        Set of all discovered subclass types, excluding ``cls`` itself.
    """
    subclasses = set(cls.__subclasses__())
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

    Uses ``inspect.isabstract`` to detect classes that have one or more
    unimplemented abstract methods and therefore cannot be instantiated directly.

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
        """Invoke the getter with the owner class and return the result.

        Args:
            obj: The instance the attribute was accessed from, or ``None``
                when accessed directly on the class. Not used.
            owner: The class through which the attribute is accessed.
        """
        return self.fget(owner)
