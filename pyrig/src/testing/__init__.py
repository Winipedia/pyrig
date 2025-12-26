"""Testing utilities and test generation infrastructure.

This package provides utilities for test creation, validation, and naming
conventions. It includes automatic test skeleton generation, assertion helpers,
and bidirectional mapping between source objects and their corresponding test
objects.

The package supports pyrig's test generation features, enabling automatic
creation of test skeletons that follow pytest conventions and maintain
consistent naming patterns across the codebase.

Modules:
    - **assertions**: Custom assertion functions with enhanced error messages
      for better test failure diagnostics
    - **convention**: Test naming conventions and object mapping utilities for
      bidirectional conversion between source and test objects

Key Features:
    - **Test naming conventions**: Consistent pytest-style naming (test_*, Test*)
    - **Object mapping**: Bidirectional mapping between source and test objects
    - **Assertion helpers**: Enhanced assertions with detailed error messages
    - **Test generation**: Utilities for automatic test skeleton creation

Example:
    >>> from pyrig.src.testing.convention import make_test_obj_name
    >>> from pyrig.src.testing.assertions import assert_with_info
    >>>
    >>> # Generate test name from source function
    >>> def my_function():
    ...     pass
    >>> make_test_obj_name(my_function)
    'test_my_function'
    >>>
    >>> # Use enhanced assertions
    >>> assert_with_info(2 + 2 == 4, expected=4, actual=4)

See Also:
    pyrig.dev.cli.subcommands.test: CLI test command
    pyrig.dev.builders.test: Test skeleton generation
"""
