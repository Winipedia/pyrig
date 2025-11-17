"""module for the following module path (maybe truncated).

tests.test_py_dev.test_testing.test_tests.test_base.test_scopes.test_module
"""

import pytest


@pytest.mark.skip(reason="Can not test a test")
def test_assert_all_funcs_and_classes_tested() -> None:
    """Test func for _test_all_funcs_and_classes_tested."""
    raise NotImplementedError
