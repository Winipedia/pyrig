"""Module-level test fixtures and utilities.

These fixtures in this module are automatically applied to all test modules
through pytest's autouse mechanism. Pyrig automatically adds this module to
pytest_plugins in conftest.py. However you still have decorate the fixture
with @autouse_module_fixture from pyrig.src.testing.fixtures or with pytest's
autouse mechanism @pytest.fixture(scope="module", autouse=True).
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
    """Verify that all functions and classes in a module have corresponding tests.

    This fixture runs automatically for each test module and checks that every
    function and class defined in the corresponding source module has a test
    function or class defined in the test module.

    Args:
        request: The pytest fixture request object containing the current module
        assert_no_untested_objs: The assert_no_untested_objs fixture asserts
            that all objects have corresponding tests

    Raises:
        AssertionError: If any function or class in the source module lacks a test

    """
    module: ModuleType = request.module
    assert_no_untested_objs(module)
