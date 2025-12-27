"""Class-scoped autouse fixtures for automatic test coverage validation.

Provides autouse fixtures that verify every method in a source class has a
corresponding test method. Runs automatically per test class.

Fixtures:
    assert_all_methods_tested: Verifies all methods have corresponding tests,
        auto-generating skeletons for missing tests.
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
    """Verify that all methods in the current test class have corresponding tests.

    Runs automatically per test class. Delegates to ``assert_no_untested_objs``
    to check coverage and generate test skeletons for missing tests.

    Args:
        request: Pytest fixture request with test class via ``request.node.cls``.
        assert_no_untested_objs: Session-scoped coverage verification callable.

    Raises:
        AssertionError: If any source method lacks a corresponding test method.

    Note:
        Skips if ``request.node.cls`` is None (function-level tests).
    """
    class_ = request.node.cls
    if class_ is None:
        return
    assert_no_untested_objs(class_)
