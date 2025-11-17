"""Inspection utilities for introspecting Python objects.

This module provides utility functions for inspecting Python objects,
including checking if an object is a function or method, and unwrapping
methods to their underlying functions.
"""

import inspect
import sys
from collections.abc import Callable
from typing import Any, cast


def get_obj_members(
    obj: Any, *, include_annotate: bool = False
) -> list[tuple[str, Any]]:
    """Get all members of an object."""
    members = [(member, value) for member, value in inspect.getmembers(obj)]
    if not include_annotate:
        members = [
            (member, value)
            for member, value in members
            if member not in ("__annotate__", "__annotate_func__")
        ]
    return members


def inside_frozen_bundle() -> bool:
    """Return True if the code is running inside a frozen bundle."""
    return getattr(sys, "frozen", False)


def get_def_line(obj: Any) -> int:
    """Return the line number where a method-like object is defined."""
    if isinstance(obj, property):
        obj = obj.fget
    unwrapped = inspect.unwrap(obj)
    if hasattr(unwrapped, "__code__"):
        return int(unwrapped.__code__.co_firstlineno)
    # getsourcelines does not work if in a pyinstaller bundle or something
    if inside_frozen_bundle():
        return 0
    return inspect.getsourcelines(unwrapped)[1]


def get_unwrapped_obj(obj: Any) -> Any:
    """Return the unwrapped version of a method-like object."""
    if isinstance(obj, property):
        obj = obj.fget  # get the getter function of the property
    return inspect.unwrap(obj)


def get_qualname_of_obj(obj: Callable[..., Any] | type) -> str:
    """Return the name of a method-like object."""
    unwrapped = get_unwrapped_obj(obj)
    return cast("str", unwrapped.__qualname__)
