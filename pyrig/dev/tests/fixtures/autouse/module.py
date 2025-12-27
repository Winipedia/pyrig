"""Module-scoped autouse fixtures for automatic test coverage validation.

Provides autouse fixtures that verify every function and class in a source
module has a corresponding test. Runs automatically per test module.

Fixtures:
    assert_all_funcs_and_classes_tested: Verifies all functions and classes
        have corresponding tests, auto-generating skeletons for missing tests.
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
    """Verify all functions and classes in the test module have corresponding tests.

    Runs automatically per test module. Delegates to ``assert_no_untested_objs``
    to check coverage and generate test skeletons for missing tests.

    Args:
        request: Pytest fixture request with test module via ``request.module``.
        assert_no_untested_objs: Session-scoped coverage verification callable.

    Raises:
        AssertionError: If any source function or class lacks a corresponding test.
    """
    module: ModuleType = request.module
    assert_no_untested_objs(module)
