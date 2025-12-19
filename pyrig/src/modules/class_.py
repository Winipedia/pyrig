"""Class introspection and subclass discovery utilities.

This module provides utilities for inspecting Python classes, extracting their
methods, and discovering subclasses across packages. The subclass discovery
system is central to pyrig's plugin architecture, enabling automatic discovery
of ConfigFile implementations, Builder subclasses, and other extensible
components.

Key features:
    - Method extraction with optional parent class filtering
    - Class discovery within modules
    - Recursive subclass discovery with package loading
    - Intelligent "leaf class" filtering via `discard_parents`

The `discard_parents` feature is particularly important: when multiple packages
define subclasses in a chain (e.g., BaseConfig -> PyrigConfig -> UserConfig),
only the most specific (leaf) classes are kept. This enables clean override
behavior where user customizations replace base implementations.

Example:
    >>> from pyrig.src.modules.class_ import get_all_nonabstract_subclasses
    >>> subclasses = get_all_nonabstract_subclasses(
    ...     ConfigFile,
    ...     load_package_before=my_package.dev.configs,
    ...     discard_parents=True
    ... )
"""

import inspect
from collections.abc import Callable
from importlib import import_module
from types import ModuleType
from typing import Any, overload

from pyrig.src.modules.function import is_func
from pyrig.src.modules.inspection import get_def_line, get_obj_members


def get_all_methods_from_cls(
    class_: type,
    *,
    exclude_parent_methods: bool = False,
    include_annotate: bool = False,
) -> list[Callable[..., Any]]:
    """Extract all methods from a class.

    Retrieves all method-like attributes from a class, including instance
    methods, static methods, class methods, and properties. Methods are
    returned sorted by their definition order in the source code.

    This is used by pyrig to generate test skeletons for each method
    in a class.

    Args:
        class_: The class to extract methods from.
        exclude_parent_methods: If True, only includes methods defined directly
            in this class, excluding inherited methods. Useful when generating
            tests only for new methods in a subclass.
        include_annotate: If False (default), excludes `__annotate__` methods
            introduced in Python 3.14.

    Returns:
        A list of callable method objects, sorted by their line number
        in the source file.

    Example:
        >>> class MyClass:
        ...     def method_a(self): pass
        ...     def method_b(self): pass
        >>> methods = get_all_methods_from_cls(MyClass)
        >>> [m.__name__ for m in methods]
        ['method_a', 'method_b']
    """
    from pyrig.src.modules.module import (  # noqa: PLC0415  # avoid circular import
        get_module_of_obj,
    )

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

    Retrieves all class objects that are defined in the specified module,
    excluding classes imported from other modules. Classes are returned
    sorted by their definition order.

    This is used by pyrig to discover classes for test skeleton generation.

    Args:
        module: The module to extract classes from. Can be a module object
            or a fully qualified module name string.

    Returns:
        A list of class types defined in the module, sorted by their
        definition order in the source file.

    Note:
        Handles edge cases like Rust-backed classes (e.g., cryptography's
        AESGCM) that may not have standard `__module__` attributes.

    Example:
        >>> import my_module
        >>> classes = get_all_cls_from_module(my_module)
        >>> [c.__name__ for c in classes]
        ['ClassA', 'ClassB']
    """
    from pyrig.src.modules.module import (  # noqa: PLC0415  # avoid circular import
        get_module_of_obj,
    )

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
) -> set[T]:
    """Recursively discover all subclasses of a class.

    Finds all direct and indirect subclasses of the given class. Because
    Python's `__subclasses__()` only returns classes that have been imported,
    you can optionally specify a package to walk (import) before discovery.

    Args:
        cls: The base class to find subclasses of.
        load_package_before: Optional package to walk before discovery. All
            modules in this package will be imported, ensuring any subclasses
            defined there are registered with Python's subclass tracking.
            When provided, results are filtered to only include classes from
            this package.
        discard_parents: If True, removes parent classes from the result when
            both a parent and its child are present. This keeps only the most
            specific (leaf) classes, enabling clean override behavior.

    Returns:
        A set of all subclasses (including the original class itself when
        `load_package_before` is not specified).

    Example:
        >>> class Base: pass
        >>> class Child(Base): pass
        >>> class GrandChild(Child): pass
        >>> get_all_subclasses(Base)
        {Base, Child, GrandChild}
        >>> get_all_subclasses(Base, discard_parents=True)
        {GrandChild}
    """
    from pyrig.src.modules.package import (  # noqa: PLC0415  # avoid circular import
        walk_package,
    )

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
    return subclasses_set


def get_all_nonabstract_subclasses[T: type](
    cls: T,
    load_package_before: ModuleType | None = None,
    *,
    discard_parents: bool = False,
) -> set[T]:
    """Find all concrete (non-abstract) subclasses of a class.

    Similar to `get_all_subclasses`, but filters out abstract classes
    (those with unimplemented abstract methods). This is the primary
    function used by pyrig to discover implementations of ConfigFile,
    Builder, and other extensible base classes.

    Args:
        cls: The base class to find subclasses of.
        load_package_before: Optional package to walk before discovery.
            See `get_all_subclasses` for details.
        discard_parents: If True, keeps only leaf classes when a parent
            and child are both present.

    Returns:
        A set of all non-abstract subclasses.

    Example:
        >>> from abc import ABC, abstractmethod
        >>> class Base(ABC):
        ...     @abstractmethod
        ...     def method(self): pass
        >>> class Concrete(Base):
        ...     def method(self): pass
        >>> get_all_nonabstract_subclasses(Base)
        {Concrete}
    """
    return {
        subclass
        for subclass in get_all_subclasses(
            cls,
            load_package_before=load_package_before,
            discard_parents=discard_parents,
        )
        if not inspect.isabstract(subclass)
    }


def init_all_nonabstract_subclasses[T: type](
    cls: T,
    load_package_before: ModuleType | None = None,
    *,
    discard_parents: bool = False,
) -> None:
    """Discover and instantiate all concrete subclasses of a class.

    Finds all non-abstract subclasses and calls their default constructor
    (no arguments). This is used by pyrig's ConfigFile and Builder systems
    to automatically initialize all discovered implementations.

    Args:
        cls: The base class to find and instantiate subclasses of.
        load_package_before: Optional package to walk before discovery.
        discard_parents: If True, only instantiates leaf classes.

    Note:
        All subclasses must have a no-argument `__init__` or be classes
        that can be called with no arguments (e.g., using `__init_subclass__`
        or `__new__` for initialization).
    """
    for subclass in get_all_nonabstract_subclasses(
        cls,
        load_package_before=load_package_before,
        discard_parents=discard_parents,
    ):
        subclass()


def get_all_nonabst_subcls_from_mod_in_all_deps_depen_on_dep[T: type](
    cls: T,
    dep: ModuleType,
    load_package_before: ModuleType,
    *,
    discard_parents: bool = False,
) -> list[T]:
    """Find non-abstract subclasses across all packages depending on a dependency.

    This is the core discovery function for pyrig's multi-package architecture.
    It finds all packages that depend on `dep`, looks for the same relative
    module path as `load_package_before` in each, and discovers subclasses
    of `cls` in those modules.

    For example, if `dep` is smth and `load_package_before` is
    `smth.dev.configs`, this will find `myapp.dev.configs` in any package
    that depends on smth, and discover ConfigFile subclasses there.

    Args:
        cls: The base class to find subclasses of.
        dep: The dependency package that other packages depend on (e.g., pyrig or smth).
        load_package_before: The module path within `dep` to use as a template
            for finding equivalent modules in dependent packages.
        discard_parents: If True, keeps only leaf classes when inheritance
            chains span multiple packages.

    Returns:
        A list of all discovered non-abstract subclasses. Classes from the
        same module are grouped together, but ordering between packages
        depends on the dependency graph traversal order.

    Example:
        >>> # Find all ConfigFile implementations across the ecosystem
        >>> subclasses = get_all_nonabst_subcls_from_mod_in_all_deps_depen_on_dep(
        ...     ConfigFile,
        ...     smth,
        ...     smth.dev.configs,
        ...     discard_parents=True
        ... )
    """
    from pyrig.src.modules.package import (  # noqa: PLC0415  # avoid circular import
        get_same_modules_from_deps_depen_on_dep,
    )

    subclasses: list[T] = []
    for pkg in get_same_modules_from_deps_depen_on_dep(load_package_before, dep):
        subclasses.extend(
            get_all_nonabstract_subclasses(
                cls,
                load_package_before=pkg,
                discard_parents=discard_parents,
            )
        )
    # as these are different modules and pks we need to discard parents again
    if discard_parents:
        subclasses = discard_parent_classes(subclasses)
    return subclasses


@overload
def discard_parent_classes[T: type](classes: list[T]) -> list[T]: ...


@overload
def discard_parent_classes[T: type](classes: set[T]) -> set[T]: ...


def discard_parent_classes[T: type](
    classes: list[T] | set[T],
) -> list[T] | set[T]:
    """Remove parent classes when their children are also present.

    Filters a collection of classes to keep only "leaf" classes - those
    that have no subclasses in the collection. This enables clean override
    behavior: if you subclass a ConfigFile, only your subclass will be used.

    Args:
        classes: A list or set of class types to filter. Modified in place.

    Returns:
        The same collection with parent classes removed. The return type
        matches the input type (list or set).

    Example:
        >>> class A: pass
        >>> class B(A): pass
        >>> class C(B): pass
        >>> discard_parent_classes({A, B, C})
        {C}
        >>> discard_parent_classes([A, C])  # B not in list, so A stays
        [A, C]
    """
    for cls in classes.copy():
        if any(child in classes for child in cls.__subclasses__()):
            classes.remove(cls)
    return classes
