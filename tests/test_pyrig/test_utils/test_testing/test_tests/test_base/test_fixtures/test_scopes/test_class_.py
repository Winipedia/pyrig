"""module for the following module path (maybe truncated).

tests.test_pyrig.test_testing.test_tests.test_base.test_scopes.test_class_
"""

import pytest


@pytest.mark.skip(reason="Can not test a test")
def test_assert_all_methods_tested() -> None:
    """Test func for _test_all_methods_tested."""
    raise NotImplementedError
