"""Class-level test fixtures and utilities.

This module provides fixtures and test functions that operate at the class scope,
ensuring that all methods within a test class have corresponding tests.
These fixtures are automatically applied to all test classes through pytest's autouse
mechanism.
"""

import pytest

from pyrig.src.testing.fixtures import autouse_class_fixture
from pyrig.src.testing.utils import assert_no_untested_objs


@autouse_class_fixture
def assert_all_methods_tested(request: pytest.FixtureRequest) -> None:
    """Verify that all methods in a class have corresponding tests.

    This fixture runs automatically for each test class and checks that every
    method defined in the corresponding source class has a test method defined
    in the test class.

    Args:
        request: The pytest fixture request object containing the current class

    Raises:
        AssertionError: If any method in the source class lacks a test

    """
    class_ = request.node.cls
    if class_ is None:
        return
    assert_no_untested_objs(class_)
