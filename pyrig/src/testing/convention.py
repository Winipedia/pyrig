"""Test naming conventions and object mapping utilities.

This module defines pyrig's test naming conventions and provides bidirectional
mapping between source objects and their corresponding test objects. The
conventions follow pytest standards and enable automatic test skeleton
generation and test-to-source navigation.

Naming Conventions:
    - **Test functions**: ``test_<function_name>``
    - **Test classes**: ``Test<ClassName>``
    - **Test modules**: ``test_<module_name>.py``
    - **Test package**: ``tests/``

The module provides utilities for:
    - **Name generation**: Convert source object names to test names
    - **Import path generation**: Create test import paths from source paths
    - **Bidirectional mapping**: Navigate between source and test objects
    - **Prefix detection**: Determine appropriate test prefix by object type

These utilities power pyrig's test generation features, enabling automatic
creation of test skeletons that follow consistent naming patterns and maintain
proper package structure.

Example:
    >>> from pyrig.src.testing.convention import (
    ...     make_test_obj_name,
    ...     make_test_obj_importpath_from_obj,
    ...     get_test_obj_from_obj
    ... )
    >>> # Generate test name from function
    >>> def my_function():
    ...     pass
    >>> make_test_obj_name(my_function)
    'test_my_function'
    >>>
    >>> # Generate test import path
    >>> make_test_obj_importpath_from_obj(my_function)
    'tests.test_module.test_my_function'
    >>>
    >>> # Get actual test object (if it exists)
    >>> test_func = get_test_obj_from_obj(my_function)

Module Attributes:
    COVERAGE_THRESHOLD (int): Minimum test coverage percentage (90%)
    TEST_FUNCTION_PREFIX (str): Prefix for test functions ("test_")
    TEST_CLASS_PREFIX (str): Prefix for test classes ("Test")
    TEST_MODULE_PREFIX (str): Prefix for test modules ("test_")
    TEST_PREFIXES (list[str]): All valid test prefixes
    TESTS_PACKAGE_NAME (str): Name of the tests package ("tests")

See Also:
    pyrig.dev.builders.test: Test skeleton generation using these conventions
    pyrig.src.testing.assertions: Assertion utilities for tests
    pyrig.src.modules.module: Module import utilities used internally
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
"""Minimum test coverage percentage threshold for pyrig projects."""

TEST_FUNCTION_PREFIX = "test_"
"""Prefix for test function names following pytest conventions."""

TEST_CLASS_PREFIX = "Test"
"""Prefix for test class names following pytest conventions."""

TEST_MODULE_PREFIX = TEST_FUNCTION_PREFIX
"""Prefix for test module names (same as function prefix)."""

TEST_PREFIXES = [TEST_FUNCTION_PREFIX, TEST_CLASS_PREFIX, TEST_MODULE_PREFIX]
"""List of all valid test prefixes for validation."""

TESTS_PACKAGE_NAME = "tests"
"""Standard name for the tests package directory."""


def get_right_test_prefix(obj: Callable[..., Any] | type | ModuleType) -> str:
    """Get the appropriate test prefix for an object based on its type.

    Determines which test naming prefix to use based on whether the object
    is a module, class, or function. This ensures consistent naming across
    different object types.

    Args:
        obj: The object to get the test prefix for. Can be:
            - ModuleType: Returns TEST_MODULE_PREFIX ("test_")
            - type (class): Returns TEST_CLASS_PREFIX ("Test")
            - Callable (function): Returns TEST_FUNCTION_PREFIX ("test_")

    Returns:
        The appropriate test prefix string for the given object type:
            - "test_" for modules and functions
            - "Test" for classes

    Example:
        >>> import types
        >>> # Module prefix
        >>> get_right_test_prefix(types.ModuleType("mymodule"))
        'test_'
        >>>
        >>> # Class prefix
        >>> class MyClass:
        ...     pass
        >>> get_right_test_prefix(MyClass)
        'Test'
        >>>
        >>> # Function prefix
        >>> def my_function():
        ...     pass
        >>> get_right_test_prefix(my_function)
        'test_'

    See Also:
        make_test_obj_name: Uses this to generate test names
    """
    if isinstance(obj, ModuleType):
        return TEST_MODULE_PREFIX
    if isinstance(obj, type):
        return TEST_CLASS_PREFIX
    return TEST_FUNCTION_PREFIX


def make_test_obj_name(obj: Callable[..., Any] | type | ModuleType) -> str:
    """Create a test name for an object by adding the appropriate prefix.

    Generates a test name following pytest conventions by prepending the
    appropriate prefix to the object's name. The prefix is determined by
    the object's type (module, class, or function).

    Args:
        obj: The object to create a test name for. Can be a module, class,
            or function.

    Returns:
        The test name with the appropriate prefix:
            - Functions: "test_<function_name>"
            - Classes: "Test<ClassName>"
            - Modules: "test_<module_name>"

    Example:
        >>> def calculate_sum(a, b):
        ...     return a + b
        >>> make_test_obj_name(calculate_sum)
        'test_calculate_sum'
        >>>
        >>> class UserManager:
        ...     pass
        >>> make_test_obj_name(UserManager)
        'TestUserManager'

    See Also:
        get_right_test_prefix: Determines which prefix to use
        reverse_make_test_obj_name: Inverse operation
    """
    prefix = get_right_test_prefix(obj)
    name = get_isolated_obj_name(obj)
    return prefix + name


def reverse_make_test_obj_name(test_name: str) -> str:
    """Extract the original object name from a test name by removing the prefix.

    Reverses the operation of `make_test_obj_name` by removing the test
    prefix from a test name to recover the original object name. This is
    used for navigating from test objects back to source objects.

    Args:
        test_name: The test name to extract the original name from. Should
            start with one of the valid test prefixes ("test_", "Test").

    Returns:
        The original object name without the test prefix. For example:
            - "test_calculate_sum" → "calculate_sum"
            - "TestUserManager" → "UserManager"

    Raises:
        ValueError: If the test name doesn't start with any of the expected
            prefixes (TEST_FUNCTION_PREFIX, TEST_CLASS_PREFIX, or
            TEST_MODULE_PREFIX).

    Example:
        >>> reverse_make_test_obj_name("test_calculate_sum")
        'calculate_sum'
        >>>
        >>> reverse_make_test_obj_name("TestUserManager")
        'UserManager'
        >>>
        >>> reverse_make_test_obj_name("invalid_name")
        Traceback (most recent call last):
            ...
        ValueError: test_name='invalid_name' is expected to start with...

    See Also:
        make_test_obj_name: Inverse operation
        make_obj_importpath_from_test_obj: Uses this for path conversion
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

    Generates the full import path for a test object by converting the source
    object's import path to follow test naming conventions. This includes:
        - Prepending "tests" package
        - Adding test prefixes to all path components
        - Maintaining the package hierarchy

    The function handles the full path from package to object, ensuring each
    component gets the appropriate test prefix based on its naming convention
    (lowercase for modules, uppercase for classes).

    Args:
        obj: The original object to create a test import path for. Can be a
            module, class, or function from the source code.

    Returns:
        The import path for the corresponding test object. For example:
            - "myapp.utils.calculate" → "tests.test_myapp.test_utils.test_calculate"
            - "myapp.models.User" → "tests.test_myapp.test_models.TestUser"

    Example:
        >>> # For a function in myapp.utils module
        >>> from myapp.utils import calculate_sum
        >>> make_test_obj_importpath_from_obj(calculate_sum)
        'tests.test_myapp.test_utils.test_calculate_sum'
        >>>
        >>> # For a class in myapp.models module
        >>> from myapp.models import User
        >>> make_test_obj_importpath_from_obj(User)
        'tests.test_myapp.test_models.TestUser'

    Note:
        The function determines whether to use TEST_MODULE_PREFIX or
        TEST_CLASS_PREFIX for each path component based on whether the
        component name starts with a lowercase letter (module) or uppercase
        letter (class).

    See Also:
        make_obj_importpath_from_test_obj: Inverse operation
        make_test_obj_name: Generates the final test name
        get_test_obj_from_obj: Uses this to import the test object
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

    Reverses the operation of `make_test_obj_importpath_from_obj` by
    converting a test object's import path back to the original source
    object's import path. This removes the "tests" package prefix and
    strips test prefixes from all path components.

    Args:
        test_obj: The test object to create an original import path for.
            Should be a test module, class, or function from the tests package.

    Returns:
        The import path for the corresponding original object. For example:
            - "tests.test_myapp.test_utils.test_calculate" → "myapp.utils.calculate"
            - "tests.test_myapp.test_models.TestUser" → "myapp.models.User"

    Example:
        >>> # For a test function
        >>> from tests.test_myapp.test_utils import test_calculate_sum
        >>> make_obj_importpath_from_test_obj(test_calculate_sum)
        'myapp.utils.calculate_sum'
        >>>
        >>> # For a test class
        >>> from tests.test_myapp.test_models import TestUser
        >>> make_obj_importpath_from_test_obj(TestUser)
        'myapp.models.User'

    Note:
        The function assumes the test object's import path starts with the
        TESTS_PACKAGE_NAME ("tests"). It removes this prefix and then
        reverses the test naming for all remaining components.

    See Also:
        make_test_obj_importpath_from_obj: Inverse operation
        reverse_make_test_obj_name: Used to strip test prefixes
        get_obj_from_test_obj: Uses this to import the source object
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
    """Get the test object corresponding to an original object.

    Dynamically imports and returns the test object that corresponds to the
    given source object. This enables navigation from source code to tests
    and is used by pyrig's test generation and validation features.

    The function:
        1. Generates the test import path using `make_test_obj_importpath_from_obj`
        2. Dynamically imports the test object from that path
        3. Returns the imported test object

    Args:
        obj: The original object to get the test object for. Can be a module,
            class, or function from the source code.

    Returns:
        The corresponding test object with the same type as the input:
            - If obj is a type (class), returns a type (test class)
            - If obj is a Callable (function), returns a Callable (test function)
            - If obj is a ModuleType (module), returns a ModuleType (test module)

    Raises:
        ImportError: If the test object doesn't exist or can't be imported.
        AttributeError: If the test object path is invalid.

    Example:
        >>> # Get test function for a source function
        >>> from myapp.utils import calculate_sum
        >>> test_func = get_test_obj_from_obj(calculate_sum)
        >>> test_func.__name__
        'test_calculate_sum'
        >>>
        >>> # Get test class for a source class
        >>> from myapp.models import User
        >>> test_class = get_test_obj_from_obj(User)
        >>> test_class.__name__
        'TestUser'

    Note:
        This function requires that the test object already exists. It's
        typically used for validation or navigation, not for test generation.

    See Also:
        get_obj_from_test_obj: Inverse operation
        make_test_obj_importpath_from_obj: Generates the import path
    """
    test_obj_path = make_test_obj_importpath_from_obj(obj)
    return import_obj_from_importpath(test_obj_path)


def get_obj_from_test_obj(
    test_obj: Callable[..., Any] | type | ModuleType,
) -> Callable[..., Any] | type | ModuleType:
    """Get the original object corresponding to a test object.

    Dynamically imports and returns the source object that corresponds to the
    given test object. This enables navigation from tests back to source code
    and is used for test validation and coverage analysis.

    The function:
        1. Generates the source import path using `make_obj_importpath_from_test_obj`
        2. Dynamically imports the source object from that path
        3. Returns the imported source object

    Args:
        test_obj: The test object to get the original object for. Should be
            a test module, class, or function from the tests package.

    Returns:
        The corresponding original object with the same type as the input:
            - If test_obj is a type (test class), returns a type (source class)
            - If test_obj is a Callable (test function), returns a Callable
              (source function)
            - If test_obj is a ModuleType (test module), returns a ModuleType
              (source module)

    Raises:
        ImportError: If the source object doesn't exist or can't be imported.
        AttributeError: If the source object path is invalid.

    Example:
        >>> # Get source function from test function
        >>> from tests.test_myapp.test_utils import test_calculate_sum
        >>> source_func = get_obj_from_test_obj(test_calculate_sum)
        >>> source_func.__name__
        'calculate_sum'
        >>>
        >>> # Get source class from test class
        >>> from tests.test_myapp.test_models import TestUser
        >>> source_class = get_obj_from_test_obj(TestUser)
        >>> source_class.__name__
        'User'

    Note:
        This function is useful for validating that tests correspond to
        actual source code and for coverage analysis.

    See Also:
        get_test_obj_from_obj: Inverse operation
        make_obj_importpath_from_test_obj: Generates the import path
    """
    obj_importpath = make_obj_importpath_from_test_obj(test_obj)
    return import_obj_from_importpath(obj_importpath)


def make_summary_error_msg(
    errors_locations: Iterable[str],
) -> str:
    """Create an error message summarizing multiple error locations.

    Formats a collection of error locations into a readable error message
    with a bulleted list. This is used for reporting multiple validation
    errors or test failures in a single message.

    Args:
        errors_locations: Collection of error location strings. Each string
            should describe where an error occurred (e.g., file paths,
            function names, line numbers).

    Returns:
        A formatted error message with the header "Found errors at:" followed
        by a bulleted list of all error locations.

    Example:
        >>> errors = [
        ...     "tests/test_utils.py::test_calculate_sum",
        ...     "tests/test_models.py::TestUser::test_save",
        ...     "tests/test_views.py::test_index"
        ... ]
        >>> print(make_summary_error_msg(errors))

            Found errors at:
                - tests/test_utils.py::test_calculate_sum
                - tests/test_models.py::TestUser::test_save
                - tests/test_views.py::test_index

    Note:
        The returned message includes leading whitespace and newlines for
        formatting. You may want to strip or adjust this based on your
        display context.

    See Also:
        pyrig.src.testing.assertions: Assertion utilities that may use this
    """
    msg = """
    Found errors at:
    """
    for error_location in errors_locations:
        msg += f"""
        - {error_location}
        """
    return msg
