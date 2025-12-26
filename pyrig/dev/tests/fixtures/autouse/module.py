"""Module-scoped autouse fixtures for automatic test coverage validation.

This module provides autouse fixtures that run automatically once per test
module to enforce test coverage at the module level. The fixtures verify that
every function and class in a source module has a corresponding test function
or test class in the test module.

The fixtures are automatically registered via pytest_plugins in conftest.py,
and they use the `@autouse_module_fixture` decorator to run automatically for
every test module without requiring explicit fixture requests.

Fixtures:
    assert_all_funcs_and_classes_tested: Autouse fixture that verifies all
        functions and classes in a source module have corresponding tests in
        the test module.

How It Works:
    1. Pytest runs this fixture automatically for each test module
    2. The fixture receives the test module via `request.module`
    3. It calls `assert_no_untested_objs()` to verify coverage
    4. If any functions/classes lack tests, test skeletons are auto-generated
    5. The test fails with a detailed error message

This ensures that:
    - Every function in a source module has a test function
    - Every class in a source module has a test class
    - Test coverage never decreases
    - New functions/classes automatically get test skeletons
    - Developers are immediately notified of missing tests

Example:
    Given this source module::

        # myapp/src/calculator.py
        def add(a, b):
            return a + b

        def subtract(a, b):
            return a - b

        class Calculator:
            pass

    And this test module::

        # tests/test_calculator.py
        def test_add():
            assert add(1, 2) == 3

        # Missing: test_subtract
        # Missing: TestCalculator

    The autouse fixture will:
    1. Detect that `test_subtract` and `TestCalculator` are missing
    2. Generate test skeletons for both
    3. Fail the test with an error message
    4. Allow the developer to fill in the generated tests

See Also:
    pyrig.dev.tests.fixtures.assertions.assert_no_untested_objs: Core assertion
    pyrig.dev.tests.fixtures.autouse.class_.assert_all_methods_tested:
        Class-level equivalent
    pyrig.dev.utils.testing.autouse_module_fixture: Decorator for autouse fixtures
"""

from collections.abc import Callable
from types import ModuleType
from typing import Any

import pytest

from pyrig.dev.utils.testing import autouse_module_fixture


@autouse_module_fixture
def assert_all_funcs_and_classes_tested(
    request: pytest.FixtureRequest,
    assert_no_untested_objs: Callable[[ModuleType | type | Callable[..., Any]], None],
) -> None:
    """Automatically verify all functions and classes in a module have tests.

    This module-scoped autouse fixture runs automatically once per test module
    and verifies that every function and class defined in the corresponding
    source module has a test function or test class defined in the test module.

    The fixture enforces 100% module-level coverage by:
    1. Extracting the test module from the pytest request object
    2. Calling `assert_no_untested_objs()` with the test module
    3. Automatically generating test skeletons for missing test functions/classes
    4. Failing with a detailed error message if any tests are missing

    Args:
        request: Pytest's fixture request object. Automatically provided by
            pytest. Contains metadata about the current test, including the
            test module via `request.module`.

        assert_no_untested_objs: Session-scoped fixture that verifies all
            objects have corresponding tests. Automatically provided by pytest
            via fixture dependency injection.

    Raises:
        AssertionError: If any function or class in the source module lacks a
            corresponding test function or test class. The error message includes
            a list of missing tests and indicates that test skeletons were
            automatically generated.

    Example:
        This fixture runs automatically, so no explicit usage is needed::

            # Source module: myapp/src/calculator.py
            def add(a, b):
                return a + b

            class Calculator:
                pass

            # Test module: tests/test_calculator.py
            # Fixture runs automatically for this module
            def test_add():
                '''This test exists, so no error.'''
                assert add(1, 2) == 3

            class TestCalculator:
                '''This test class exists, so no error.'''
                pass

        If a function or class is missing::

            # Source module: myapp/src/calculator.py
            def add(a, b):
                return a + b

            def subtract(a, b):  # New function
                return a - b

            class Calculator:  # Existing class
                pass

            # Test module: tests/test_calculator.py
            def test_add():
                pass

            class TestCalculator:
                pass

            # Missing: test_subtract

            # Fixture automatically:
            # 1. Detects missing test_subtract
            # 2. Generates test skeleton
            # 3. Fails with error message

    Note:
        - This fixture runs automatically for every test module
        - Test skeletons are generated in the test file
        - The fixture uses pyrig's naming convention to map test modules to
          source modules
        - If the source module doesn't exist (custom test module), it's skipped

    See Also:
        pyrig.dev.tests.fixtures.assertions.assert_no_untested_objs: Core logic
        pyrig.dev.tests.fixtures.autouse.class_.assert_all_methods_tested:
            Class-level equivalent
        pyrig.dev.utils.testing.autouse_module_fixture: Decorator
    """
    module: ModuleType = request.module
    assert_no_untested_objs(module)
