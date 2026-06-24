"""Utilities for inspecting Python objects."""

import inspect
from collections.abc import Callable, Iterable, Iterator
from types import ModuleType
from typing import Any, cast


def obj_members(
    obj: Any, predicate: Callable[[Any], bool] | None = None
) -> Iterator[tuple[str, Any]]:
    """Yield the members of an object as name-value pairs without invoking descriptors.

    Members are read statically, so properties with side effects are not
    triggered. `__annotate__` and `__annotate_func__` are always excluded
    from the result.

    Args:
        obj: Object to inspect (class, module, or any Python object).
        predicate: Optional filter. When given, only members for which it
            returns `True` are included.

    Yields:
        `(name, value)` pairs for the matching members of `obj`.
    """
    return (
        (member, value)
        for member, value in inspect.getmembers_static(obj, predicate=predicate)
        if member not in ("__annotate__", "__annotate_func__")
    )


def sorted_by_def_line(objs: Iterable[Any]) -> list[Any]:
    """Sort objects by their source definition line number.

    Args:
        objs: Iterable of objects to sort (functions, methods, properties, etc.).

    Returns:
        New list of objects sorted ascending by their definition line number.
    """
    return sorted(objs, key=def_line)


def def_line(obj: Any) -> int:
    """Return the 1-based source line where an object is defined.

    The object is unwrapped first, so the line of the underlying function is
    returned even for properties, classmethods, staticmethods, and decorated
    callables rather than the line of a wrapper.

    Args:
        obj: Callable (function, method, property, staticmethod, classmethod,
            or decorated callable).

    Returns:
        1-based line number of the first line of the object's definition.

    Raises:
        OSError: If the source cannot be located, for example when the source
            file is missing or unavailable.
        TypeError: If the object is a built-in or C extension callable whose
            source cannot be retrieved.
    """
    unwrapped = unwrapped_obj(obj)
    if hasattr(unwrapped, "__code__"):
        return int(unwrapped.__code__.co_firstlineno)
    return inspect.getsourcelines(unwrapped)[1]


def obj_qualname(obj: Callable[..., Any] | type) -> str:
    """Return the qualified name of a callable or type.

    Unwraps the object first, so the name of the original function is returned
    rather than the name of a wrapper or descriptor. For methods, the qualified
    name includes the enclosing class, for example `"MyClass.my_method"`.

    Args:
        obj: Callable or type, optionally wrapped by a descriptor or decorator.

    Returns:
        The `__qualname__` of the underlying callable or type.
    """
    unwrapped = unwrapped_obj(obj)
    return cast("str", unwrapped.__qualname__)


def obj_module(obj: Any, default: ModuleType | None = None) -> ModuleType:
    """Return the module where a method-like object is defined.

    Unwraps the object first, so decorated functions, properties, classmethods,
    and staticmethods all resolve to their defining module. Useful for
    distinguishing objects defined in a module from those merely imported into
    it.

    Args:
        obj: Method-like object (function, method, property, staticmethod,
            classmethod, or decorated callable).
        default: Module to return when the origin cannot be determined. When
            `None` and the module cannot be determined, `LookupError` is raised.

    Returns:
        The module where `obj` is defined.

    Raises:
        LookupError: If the defining module cannot be determined and `default`
            is `None`.
    """
    module = inspect.getmodule(unwrapped_obj(obj)) or default
    if module is None:
        msg = f"Could not determine module of {obj}"
        raise LookupError(msg)
    return module


def unwrapped_obj(obj: Any) -> Any:
    """Unwrap a method-like object to its underlying function.

    Strips every layer until no more can be removed: the bound-method,
    classmethod, and staticmethod descriptors (`__func__`), the property getter
    (`fget`), and `functools.wraps`-style decorator chains. For a property, the
    getter function is returned.

    Args:
        obj: Callable that may be wrapped (bound method, property,
            staticmethod, classmethod, or any decorated function).

    Returns:
        The underlying unwrapped function object.
    """
    prev = None
    while prev is not obj:
        prev = obj
        if func := getattr(obj, "__func__", None):
            obj = func
        if fget := getattr(obj, "fget", None):
            obj = fget
        obj = inspect.unwrap(obj)
    return obj
