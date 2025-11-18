"""Testing conventions and utilities.

This module provides functions and constants for managing test naming conventions,
mapping between test objects and their corresponding implementation objects,
and utilities for test discovery and validation.

Returns:
    Various utility functions and constants for testing conventions.

"""

from collections.abc import Callable, Iterable
from types import ModuleType
from typing import Any

from pyrig.src.modules.module import (
    get_isolated_obj_name,
    import_obj_from_importpath,
    make_obj_importpath,
)

TEST_FUNCTION_PREFIX = "test_"

TEST_CLASS_PREFIX = "Test"

TEST_MODULE_PREFIX = TEST_FUNCTION_PREFIX

TEST_PREFIXES = [TEST_FUNCTION_PREFIX, TEST_CLASS_PREFIX, TEST_MODULE_PREFIX]

TESTS_PACKAGE_NAME = "tests"


def get_right_test_prefix(obj: Callable[..., Any] | type | ModuleType) -> str:
    """Get the appropriate test prefix for an object based on its type.

    Args:
        obj: The object to get the test prefix for (function, class, or module)

    Returns:
        The appropriate test prefix string for the given object type

    """
    if isinstance(obj, ModuleType):
        return TEST_MODULE_PREFIX
    if isinstance(obj, type):
        return TEST_CLASS_PREFIX
    return TEST_FUNCTION_PREFIX


def make_test_obj_name(obj: Callable[..., Any] | type | ModuleType) -> str:
    """Create a test name for an object by adding the appropriate prefix.

    Args:
        obj: The object to create a test name for

    Returns:
        The test name with the appropriate prefix

    """
    prefix = get_right_test_prefix(obj)
    name = get_isolated_obj_name(obj)
    return prefix + name


def reverse_make_test_obj_name(test_name: str) -> str:
    """Extract the original object name from a test name by removing the prefix.

    Args:
        test_name: The test name to extract the original name from

    Returns:
        The original object name without the test prefix

    Raises:
        ValueError: If the test name doesn't start with any of the expected prefixes

    """
    for prefix in TEST_PREFIXES:
        if test_name.startswith(prefix):
            return test_name.removeprefix(prefix)
    msg = f"{test_name=} is expected to start with one of {TEST_PREFIXES=}"
    raise ValueError(msg)


def make_test_obj_importpath_from_obj(
    obj: Callable[..., Any] | type | ModuleType,
) -> str:
    """Create an import path for a test object based on the original object.

    Args:
        obj: The original object to create a test import path for

    Returns:
        The import path for the corresponding test object

    """
    parts = make_obj_importpath(obj).split(".")
    test_name = make_test_obj_name(obj)
    test_parts = [
        (TEST_MODULE_PREFIX if part[0].islower() else TEST_CLASS_PREFIX) + part
        for part in parts
    ]
    test_parts[-1] = test_name
    test_parts.insert(0, TESTS_PACKAGE_NAME)
    return ".".join(test_parts)


def make_obj_importpath_from_test_obj(
    test_obj: Callable[..., Any] | type | ModuleType,
) -> str:
    """Create an import path for an original object based on its test object.

    Args:
        test_obj: The test object to create an original import path for

    Returns:
        The import path for the corresponding original object

    """
    test_parts = make_obj_importpath(test_obj).split(".")
    test_parts = test_parts[1:]
    parts = [reverse_make_test_obj_name(part) for part in test_parts]
    return ".".join(parts)


def get_test_obj_from_obj(
    obj: Callable[..., Any] | type | ModuleType,
) -> Callable[..., Any] | type | ModuleType:
    """Get the test object corresponding to an original object.

    Args:
        obj: The original object to get the test object for

    Returns:
        The corresponding test object

    """
    test_obj_path = make_test_obj_importpath_from_obj(obj)
    return import_obj_from_importpath(test_obj_path)


def get_obj_from_test_obj(
    test_obj: Callable[..., Any] | type | ModuleType,
) -> Callable[..., Any] | type | ModuleType:
    """Get the original object corresponding to a test object.

    Args:
        test_obj: The test object to get the original object for

    Returns:
        The corresponding original object

    """
    obj_importpath = make_obj_importpath_from_test_obj(test_obj)
    return import_obj_from_importpath(obj_importpath)


def make_untested_summary_error_msg(
    untested_objs: Iterable[str],
) -> str:
    """Create an error message summarizing untested objects.

    Args:
        untested_objs: Collection of import paths for untested objects

    Returns:
        A formatted error message listing all untested objects

    """
    msg = """
    Found untested objects:
    """
    for untested in untested_objs:
        msg += f"""
        - {untested}
        """
    return msg
