"""Low-level inspection utilities for Python object introspection.

Provides foundational utilities for inspecting Python objects, unwrapping decorated
methods, and accessing object metadata. Handles properties, staticmethods, classmethods,
and decorator chains.
"""

import inspect
from collections.abc import Callable, Generator, Iterable
from types import ModuleType
from typing import Any, cast


def obj_members(
    obj: Any, predicate: Callable[[Any], bool] | None = None
) -> Generator[tuple[str, Any], None, None]:
    """Get all members of an object as name-value pairs using static introspection.

    Uses ``inspect.getmembers_static`` to retrieve members without invoking
    descriptors, making it safe for classes with properties that have side effects.
    Filters out ``__annotate__`` and ``__annotate_func__``, which are CPython
    implementation attributes introduced in Python 3.14 and not meaningful for
    general introspection.

    Args:
        obj: Object to inspect (class, module, or any Python object).
        predicate: Optional callable to filter members. Only members for which
            the predicate returns ``True`` are included.

    Yields:
        ``(name, value)`` tuples for all matching members of ``obj``.
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
    """Return the 1-based source line number where an object is defined.

    Handles the full range of method-like forms before resolving the line:

    - All forms: delegates to ``unwrapped_obj`` to strip property, classmethod,
      staticmethod, and ``functools.wraps`` decorator layers.

    After unwrapping, the line number is read from ``__code__.co_firstlineno``
    when available (all pure-Python callables). If that attribute is absent,
    ``inspect.getsourcelines`` is used as a fallback.

    Args:
        obj: Callable object (function, method, property, staticmethod,
            classmethod, or decorated callable).

    Returns:
        1-based line number of the first line of the object's definition.

    Raises:
        OSError: If source lines cannot be retrieved, for example for built-in
            or C extension callables that lack ``__code__``.
    """
    unwrapped = unwrapped_obj(obj)
    if hasattr(unwrapped, "__code__"):
        return int(unwrapped.__code__.co_firstlineno)
    return inspect.getsourcelines(unwrapped)[1]


def obj_qualname(obj: Callable[..., Any] | type) -> str:
    """Return the qualified name of a callable or type.

    Unwraps the object first so that the name of the original function is
    returned rather than the name of a wrapper or descriptor. For methods,
    the qualified name includes the enclosing class, for example
    ``"MyClass.my_method"``.

    Args:
        obj: Callable or type, optionally wrapped by a descriptor or decorator.

    Returns:
        The ``__qualname__`` of the underlying callable or type.
    """
    unwrapped = unwrapped_obj(obj)
    return cast("str", unwrapped.__qualname__)


def obj_module(obj: Any, default: ModuleType | None = None) -> ModuleType:
    """Return the module where a method-like object is defined.

    Unwraps the object before calling ``inspect.getmodule``, so decorated
    functions, properties, classmethods, and staticmethods are all resolved
    to their defining module correctly. Used to distinguish objects defined
    in a module from those that were merely imported into it.

    Args:
        obj: Method-like object (function, method, property, staticmethod,
            classmethod, or decorated callable).
        default: Module to return when ``inspect.getmodule`` cannot determine
            the origin. If ``None`` and the module cannot be determined, a
            ``LookupError`` is raised.

    Returns:
        The ``ModuleType`` where ``obj`` is defined.

    Raises:
        LookupError: If the defining module cannot be determined and
            ``default`` is not provided.
    """
    unwrapped = unwrapped_obj(obj)
    module = inspect.getmodule(unwrapped)
    if not module:
        msg = f"Could not determine module of {obj}"
        if default:
            return default
        raise LookupError(msg)
    return module


def unwrapped_obj(obj: Any) -> Any:
    """Unwrap a method-like object to its underlying function.

    Iteratively strips wrapping layers until the object is fully unwrapped,
    applying each of the following steps on every iteration:

    1. ``__func__``: present on bound methods, ``classmethod``, and
       ``staticmethod`` descriptors; extracts the raw function.
    2. ``fget``: present on ``property`` objects; extracts the getter function.
    3. ``inspect.unwrap``: traverses ``functools.wraps`` (and any other
       ``__wrapped__``-based) decorator chains.

    The loop exits when a full iteration produces no change, meaning no further
    layers can be removed.

    Args:
        obj: Callable that may be wrapped (bound method, property,
            staticmethod, classmethod, or any decorated function).

    Returns:
        The underlying unwrapped function object.
    """
    prev = None
    while prev is not obj:
        prev = obj
        if hasattr(obj, "__func__"):
            obj = obj.__func__
        if hasattr(obj, "fget"):
            obj = obj.fget
        obj = inspect.unwrap(obj)
    return obj
