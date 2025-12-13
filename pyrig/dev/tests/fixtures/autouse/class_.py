"""Class-level test fixtures and utilities.

These fixtures in this module are automatically applied to all test classes
through pytest's autouse mechanism. Pyrig automatically adds this module to
pytest_plugins in conftest.py. However you still have decorate the fixture
with @autouse_class_fixture from pyrig.src.testing.fixtures or with pytest's
autouse mechanism @pytest.fixture(scope="class", autouse=True).
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
    """Verify that all methods in a class have corresponding tests.

    This fixture runs automatically for each test class and checks that every
    method defined in the corresponding source class has a test method defined
    in the test class.

    Args:
        request: The pytest fixture request object containing the current class
        assert_no_untested_objs: The assert_no_untested_objs fixture asserts
            that all objects have corresponding tests

    Raises:
        AssertionError: If any method in the source class lacks a test

    """
    class_ = request.node.cls
    if class_ is None:
        return
    assert_no_untested_objs(class_)
