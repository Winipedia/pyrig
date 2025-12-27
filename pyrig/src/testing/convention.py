"""Test naming conventions and object mapping.

Defines pyrig's test naming conventions and bidirectional mapping between source
and test objects. Follows pytest standards for automatic test skeleton generation.

Naming Conventions:
    - Test functions: test_<function_name>
    - Test classes: Test<ClassName>
    - Test modules: test_<module_name>.py
    - Test package: tests/

Utilities:
    - Name generation: Convert source names to test names
    - Import path generation: Create test import paths
    - Bidirectional mapping: Navigate between source and test objects
    - Prefix detection: Determine test prefix by object type

Example:
    >>> from pyrig.src.testing.convention import make_test_obj_name
    >>> def my_function(): pass
    >>> make_test_obj_name(my_function)  # 'test_my_function'

Attributes:
    COVERAGE_THRESHOLD: Minimum test coverage percentage (90%)
    TEST_FUNCTION_PREFIX: Prefix for test functions ("test_")
    TEST_CLASS_PREFIX: Prefix for test classes ("Test")
    TEST_MODULE_PREFIX: Prefix for test modules ("test_")
    TEST_PREFIXES: All valid test prefixes
    TESTS_PACKAGE_NAME: Tests package name ("tests")
"""

from collections.abc import Callable, Iterable
from types import ModuleType
from typing import Any, overload

from pyrig.src.modules.module import (
    get_isolated_obj_name,
    import_obj_from_importpath,
    make_obj_importpath,
)

COVERAGE_THRESHOLD = 90
"""Minimum test coverage percentage threshold."""

TEST_FUNCTION_PREFIX = "test_"
"""Prefix for test function names."""

TEST_CLASS_PREFIX = "Test"
"""Prefix for test class names."""

TEST_MODULE_PREFIX = TEST_FUNCTION_PREFIX
"""Prefix for test module names."""

TEST_PREFIXES = [TEST_FUNCTION_PREFIX, TEST_CLASS_PREFIX, TEST_MODULE_PREFIX]
"""All valid test prefixes."""

TESTS_PACKAGE_NAME = "tests"
"""Tests package directory name."""


def get_right_test_prefix(obj: Callable[..., Any] | type | ModuleType) -> str:
    """Get appropriate test prefix for object based on type.

    Args:
        obj: Object to get prefix for (ModuleType, type, or Callable).

    Returns:
        Test prefix: "test_" for modules/functions, "Test" for classes.

    Example:
        >>> class MyClass: pass
        >>> get_right_test_prefix(MyClass)  # 'Test'
    """
    if isinstance(obj, ModuleType):
        return TEST_MODULE_PREFIX
    if isinstance(obj, type):
        return TEST_CLASS_PREFIX
    return TEST_FUNCTION_PREFIX


def make_test_obj_name(obj: Callable[..., Any] | type | ModuleType) -> str:
    """Create test name by adding appropriate prefix.

    Args:
        obj: Object to create test name for (module, class, or function).

    Returns:
        Test name with prefix (e.g., "test_<name>" or "Test<Name>").

    Example:
        >>> def calculate_sum(a, b): return a + b
        >>> make_test_obj_name(calculate_sum)  # 'test_calculate_sum'
    """
    prefix = get_right_test_prefix(obj)
    name = get_isolated_obj_name(obj)
    return prefix + name


def reverse_make_test_obj_name(test_name: str) -> str:
    """Extract original object name from test name by removing prefix.

    Args:
        test_name: Test name to extract from (should start with test prefix).

    Returns:
        Original object name without prefix.

    Raises:
        ValueError: If test name doesn't start with expected prefix.

    Example:
        >>> reverse_make_test_obj_name("test_calculate_sum")  # 'calculate_sum'
        >>> reverse_make_test_obj_name("TestUserManager")  # 'UserManager'
    """
    for prefix in TEST_PREFIXES:
        if test_name.startswith(prefix):
            return test_name.removeprefix(prefix)
    msg = f"{test_name=} is expected to start with one of {TEST_PREFIXES=}"
    raise ValueError(msg)


def make_test_obj_importpath_from_obj(
    obj: Callable[..., Any] | type | ModuleType,
) -> str:
    """Create test import path from original object.

    Converts source object's import path to test naming conventions:
    prepends "tests" package and adds test prefixes to all components.

    Args:
        obj: Original object (module, class, or function).

    Returns:
        Test import path (e.g., "tests.test_myapp.test_utils.test_calculate").

    Example:
        >>> from myapp.utils import calculate_sum
        >>> make_test_obj_importpath_from_obj(calculate_sum)
        'tests.test_myapp.test_utils.test_calculate_sum'
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
    """Create original import path from test object.

    Reverses make_test_obj_importpath_from_obj by removing "tests" prefix
    and stripping test prefixes from all components.

    Args:
        test_obj: Test object (module, class, or function).

    Returns:
        Original import path (e.g., "myapp.utils.calculate").

    Example:
        >>> from tests.test_myapp.test_utils import test_calculate_sum
        >>> make_obj_importpath_from_test_obj(test_calculate_sum)
        'myapp.utils.calculate_sum'
    """
    test_parts = make_obj_importpath(test_obj).split(".")
    test_parts = test_parts[1:]  # Remove "tests" prefix
    parts = [reverse_make_test_obj_name(part) for part in test_parts]
    return ".".join(parts)


@overload
def get_test_obj_from_obj(obj: type) -> type: ...


@overload
def get_test_obj_from_obj(obj: Callable[..., Any]) -> Callable[..., Any]: ...


@overload
def get_test_obj_from_obj(obj: ModuleType) -> ModuleType: ...


def get_test_obj_from_obj(
    obj: Callable[..., Any] | type | ModuleType,
) -> Callable[..., Any] | type | ModuleType:
    """Get test object corresponding to original object.

    Dynamically imports test object from generated test import path.

    Args:
        obj: Original object (module, class, or function).

    Returns:
        Corresponding test object (same type as input).

    Raises:
        ImportError: If test object doesn't exist or can't be imported.
        AttributeError: If test object path is invalid.

    Example:
        >>> from myapp.utils import calculate_sum
        >>> test_func = get_test_obj_from_obj(calculate_sum)
        >>> test_func.__name__  # 'test_calculate_sum'
    """
    test_obj_path = make_test_obj_importpath_from_obj(obj)
    return import_obj_from_importpath(test_obj_path)


def get_obj_from_test_obj(
    test_obj: Callable[..., Any] | type | ModuleType,
) -> Callable[..., Any] | type | ModuleType:
    """Get original object corresponding to test object.

    Dynamically imports source object from generated source import path.

    Args:
        test_obj: Test object (module, class, or function).

    Returns:
        Corresponding original object (same type as input).

    Raises:
        ImportError: If source object doesn't exist or can't be imported.
        AttributeError: If source object path is invalid.

    Example:
        >>> from tests.test_myapp.test_utils import test_calculate_sum
        >>> source_func = get_obj_from_test_obj(test_calculate_sum)
        >>> source_func.__name__  # 'calculate_sum'
    """
    obj_importpath = make_obj_importpath_from_test_obj(test_obj)
    return import_obj_from_importpath(obj_importpath)


def make_summary_error_msg(
    errors_locations: Iterable[str],
) -> str:
    """Create error message summarizing multiple error locations.

    Formats error locations into bulleted list for reporting validation errors.

    Args:
        errors_locations: Collection of error location strings.

    Returns:
        Formatted error message with "Found errors at:" header and bulleted list.

    Example:
        >>> errors = ["tests/test_utils.py::test_sum", "tests/test_models.py::TestUser"]
        >>> print(make_summary_error_msg(errors))
        # Found errors at:
        #     - tests/test_utils.py::test_sum
        #     - tests/test_models.py::TestUser
    """
    msg = """
    Found errors at:
    """
    for error_location in errors_locations:
        msg += f"""
        - {error_location}
        """
    return msg
