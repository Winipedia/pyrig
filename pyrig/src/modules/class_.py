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
        List of method objects sorted by line number.
        ['method_a', 'method_b']
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

    Python's `__subclasses__()` only returns imported classes. Optionally specify a
    package to walk (import) before discovery.

    Args:
        cls: Base class to find subclasses of.
        load_package_before: Optional package to walk before discovery.
            When provided, results are filtered to classes from this package.
        discard_parents: If True, keeps only leaf classes.
        exclude_abstract: If True, excludes abstract classes.

    Returns:
        Set of all subclasses.
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
    Enables clean override behavior.

    Args:
        classes: List or set of class types to filter (modified in place).

    Returns:
        Same collection with parent classes removed.
    """
    for cls in classes.copy():
        if any(child in classes for child in cls.__subclasses__()):
            classes.remove(cls)
    return classes


@cache
def get_cached_instance[T](cls: type[T]) -> T:
    """Get a cached instance of a class.

    Args:
        cls: Class to instantiate.

    Returns:
        Cached instance.
    """
    return cls()
