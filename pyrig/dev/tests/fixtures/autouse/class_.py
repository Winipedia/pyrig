"""Class-scoped autouse fixtures for automatic test coverage validation.

This module provides autouse fixtures that run automatically once per test
class to enforce test coverage at the class level. The fixtures verify that
every method in a source class has a corresponding test method in the test class.

The fixtures are automatically registered via pytest_plugins in conftest.py,
and they use the `@autouse_class_fixture` decorator to run automatically for
every test class without requiring explicit fixture requests.

Fixtures:
    assert_all_methods_tested: Autouse fixture that verifies all methods in a
        source class have corresponding test methods in the test class.

How It Works:
    1. Pytest runs this fixture automatically for each test class
    2. The fixture receives the test class via `request.node.cls`
    3. It calls `assert_no_untested_objs()` to verify coverage
    4. If any methods lack tests, test skeletons are auto-generated
    5. The test fails with a detailed error message

This ensures that:
    - Every method in a source class has a test method
    - Test coverage never decreases
    - New methods automatically get test skeletons
    - Developers are immediately notified of missing tests

Example:
    Given this source class::

        class Calculator:
            def add(self, a, b):
                return a + b

            def subtract(self, a, b):
                return a - b

    And this test class::

        class TestCalculator:
            def test_add(self):
                calc = Calculator()
                assert calc.add(1, 2) == 3

            # Missing: test_subtract

    The autouse fixture will:
    1. Detect that `test_subtract` is missing
    2. Generate a test skeleton for `test_subtract`
    3. Fail the test with an error message
    4. Allow the developer to fill in the generated test

See Also:
    pyrig.dev.tests.fixtures.assertions.assert_no_untested_objs: Core assertion
    pyrig.dev.tests.fixtures.autouse.module.assert_all_funcs_and_classes_tested:
        Module-level equivalent
    pyrig.dev.utils.testing.autouse_class_fixture: Decorator for autouse fixtures
"""

from collections.abc import Callable
from types import ModuleType
from typing import Any

import pytest

from pyrig.dev.utils.testing import autouse_class_fixture


@autouse_class_fixture
def assert_all_methods_tested(
    request: pytest.FixtureRequest,
    assert_no_untested_objs: Callable[[ModuleType | type | Callable[..., Any]], None],
) -> None:
    """Automatically verify that all methods in a class have corresponding tests.

    This class-scoped autouse fixture runs automatically once per test class
    and verifies that every method defined in the corresponding source class
    has a test method defined in the test class.

    The fixture enforces 100% method coverage by:
    1. Extracting the test class from the pytest request object
    2. Calling `assert_no_untested_objs()` with the test class
    3. Automatically generating test skeletons for missing test methods
    4. Failing with a detailed error message if any tests are missing

    Args:
        request: Pytest's fixture request object. Automatically provided by
            pytest. Contains metadata about the current test, including the
            test class via `request.node.cls`.

        assert_no_untested_objs: Session-scoped fixture that verifies all
            objects have corresponding tests. Automatically provided by pytest
            via fixture dependency injection.

    Raises:
        AssertionError: If any method in the source class lacks a corresponding
            test method. The error message includes a list of missing tests and
            indicates that test skeletons were automatically generated.

    Example:
        This fixture runs automatically, so no explicit usage is needed::

            # Source class
            class Calculator:
                def add(self, a, b):
                    return a + b

            # Test class - fixture runs automatically
            class TestCalculator:
                def test_add(self):
                    '''This test exists, so no error.'''
                    calc = Calculator()
                    assert calc.add(1, 2) == 3

        If a method is missing::

            # Source class
            class Calculator:
                def add(self, a, b):
                    return a + b

                def subtract(self, a, b):  # New method
                    return a - b

            # Test class
            class TestCalculator:
                def test_add(self):
                    pass
                # Missing: test_subtract

            # Fixture automatically:
            # 1. Detects missing test_subtract
            # 2. Generates test skeleton
            # 3. Fails with error message

    Note:
        - This fixture runs automatically for every test class
        - It skips if `request.node.cls` is None (function-level tests)
        - Test skeletons are generated in the test file
        - The fixture uses pyrig's naming convention to map test classes to
          source classes

    See Also:
        pyrig.dev.tests.fixtures.assertions.assert_no_untested_objs: Core logic
        pyrig.dev.tests.fixtures.autouse.module.assert_all_funcs_and_classes_tested:
            Module-level equivalent
        pyrig.dev.utils.testing.autouse_class_fixture: Decorator
    """
    class_ = request.node.cls
    if class_ is None:
        return
    assert_no_untested_objs(class_)
