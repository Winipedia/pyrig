"""Class introspection and subclass discovery utilities.

Utilities for inspecting classes, extracting methods, and discovering subclasses across
packages. Central to pyrig's plugin architecture for automatic discovery of ConfigFile
implementations and BuilderConfigFile subclasses.
"""

import inspect
import logging
from collections.abc import Callable
from functools import cache
from importlib import import_module
from types import ModuleType
from typing import Any, overload

from pyrig.src.modules.function import is_func
from pyrig.src.modules.imports import walk_package
from pyrig.src.modules.inspection import (
    get_def_line,
    get_module_of_obj,
    get_obj_members,
)

logger = logging.getLogger(__name__)


def get_all_methods_from_cls(
    class_: type,
    *,
    exclude_parent_methods: bool = False,
    include_annotate: bool = False,
) -> list[Callable[..., Any]]:
    """Extract all methods from a class.

    Includes instance methods, static methods, class methods, and properties.
    Returns methods sorted by definition order.

    Args:
        class_: Class to extract methods from.
        exclude_parent_methods: If True, excludes inherited methods.
        include_annotate: If False, excludes `__annotate__` (Python 3.14+).

    Returns:
        List of method objects (Callable) sorted by line number.
    """
    methods = [
        (method, name)
        for name, method in get_obj_members(class_, include_annotate=include_annotate)
        if is_func(method)
    ]

    if exclude_parent_methods:
        methods = [
            (method, name)
            for method, name in methods
            if get_module_of_obj(method).__name__ == class_.__module__
            and name in class_.__dict__
        ]

    only_methods = [method for method, _name in methods]
    # sort by definition order
    return sorted(only_methods, key=get_def_line)


def get_all_cls_from_module(module: ModuleType | str) -> list[type]:
    """Extract all classes defined directly in a module.

    Args:
        module: Module object or fully qualified module name.

    Returns:
        List of class types sorted by definition order.

    Note:
        Handles edge cases like Rust-backed classes (e.g., cryptography's AESGCM).
    """
    if isinstance(module, str):
        module = import_module(module)

    # necessary for bindings packages like AESGCM from cryptography._rust backend
    default = ModuleType("default")
    classes = [
        obj
        for _, obj in inspect.getmembers(module, inspect.isclass)
        if get_module_of_obj(obj, default).__name__ == module.__name__
    ]
    # sort by definition order
    return sorted(classes, key=get_def_line)


def get_all_subclasses[T: type](
    cls: T,
    load_package_before: ModuleType | None = None,
    *,
    discard_parents: bool = False,
    exclude_abstract: bool = False,
) -> set[T]:
    """Recursively discover all subclasses of a class.

    Python's ``__subclasses__()`` method only returns classes that have been
    imported into the interpreter. This function addresses that limitation by
    optionally walking (importing) a package before discovery, ensuring all
    subclasses defined in that package are visible.

    The discovery process:
        1. If ``load_package_before`` is provided, recursively imports all
           modules in that package (triggering class registration)
        2. Recursively collects all subclasses via ``__subclasses__()``
        3. If ``load_package_before`` was provided, filters results to only
           include classes whose ``__module__`` contains the package name
        4. Optionally removes parent classes (keeping only leaves)
        5. Optionally removes abstract classes

    Args:
        cls: Base class to find subclasses of. The base class itself is
            included in the results.
        load_package_before: Package to walk (import) before discovery.
            When provided, all modules in this package are imported to ensure
            subclasses are registered with Python. Results are then filtered
            to only include classes from this package.
        discard_parents: If True, removes classes that have subclasses also
            in the result set, keeping only "leaf" classes. Useful for
            override patterns where you want only the most derived class.
        exclude_abstract: If True, removes classes with unimplemented
            abstract methods (``inspect.isabstract()`` returns True).

    Returns:
        Set of discovered subclass types (including ``cls`` itself unless
        filtered out by other options).

    Example:
        >>> # Discover all ConfigFile subclasses in myapp.dev.configs
        >>> from myapp.dev import configs
        >>> subclasses = get_all_subclasses(
        ...     ConfigFile,
        ...     load_package_before=configs,
        ...     discard_parents=True,
        ...     exclude_abstract=True,
        ... )

    Note:
        The recursive ``__subclasses__()`` traversal finds the complete
        inheritance tree, not just direct children. This is essential for
        discovering deeply nested subclasses.

    See Also:
        discard_parent_classes: Logic for filtering to leaf classes only
        walk_package: Package traversal that triggers imports
    """
    logger.debug("Discovering subclasses of %s", cls.__name__)
    if load_package_before:
        _ = list(walk_package(load_package_before))
    subclasses_set: set[T] = {cls}
    subclasses_set.update(cls.__subclasses__())
    for subclass in cls.__subclasses__():
        subclasses_set.update(get_all_subclasses(subclass))
    if load_package_before is not None:
        # remove all not in the package
        subclasses_set = {
            subclass
            for subclass in subclasses_set
            if load_package_before.__name__ in subclass.__module__
        }
    if discard_parents:
        subclasses_set = discard_parent_classes(subclasses_set)

    if exclude_abstract:
        subclasses_set = {
            subclass for subclass in subclasses_set if not inspect.isabstract(subclass)
        }
    return subclasses_set


@overload
def discard_parent_classes[T: type](classes: list[T]) -> list[T]: ...


@overload
def discard_parent_classes[T: type](classes: set[T]) -> set[T]: ...


def discard_parent_classes[T: type](
    classes: list[T] | set[T],
) -> list[T] | set[T]:
    """Remove parent classes when their children are also present.

    Keeps only "leaf" classes - those with no subclasses in the collection.
    Enables clean override behavior where derived classes override base implementations.

    Args:
        classes: List or set of class types to filter. The collection is modified
            in place (elements are removed from the original collection).

    Returns:
        The same collection instance with parent classes removed.
    """
    for cls in classes.copy():
        if any(child in classes for child in cls.__subclasses__()):
            classes.remove(cls)
    return classes


@cache
def get_cached_instance[T](cls: type[T]) -> T:
    """Get or create a cached singleton instance of a class.

    Uses ``functools.cache`` to memoize class instantiation. The first call
    creates the instance, subsequent calls return the same cached instance.
    Enables singleton-like patterns without explicit singleton implementation.

    Args:
        cls: Class to instantiate. Must be callable with no arguments.

    Returns:
        Cached instance of the class. Same instance is returned on repeated calls.

    Example:
        >>> class ExpensiveResource:
        ...     def __init__(self):
        ...         print("Creating resource...")
        ...
        >>> get_cached_instance(ExpensiveResource)  # prints "Creating resource..."
        >>> get_cached_instance(ExpensiveResource)  # returns cached, no print
    """
    return cls()


class classproperty[T]:  # noqa: N801
    """Decorator that creates a property accessible on the class itself.

    Unlike @property which only works on instances, @classproperty allows
    accessing the property directly on the class. Can be combined with
    caching by using @cache on the underlying method.

    Example:
        >>> class MyClass:
        ...     @classproperty
        ...     def name(cls) -> str:
        ...         return cls.__name__.lower()
        ...
        >>> MyClass.name
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
