"""Tests module."""

from pyrig.src.testing.utils import (
    assert_no_untested_objs,
)
from tests.test_pyrig.test_src.test_testing import test_assertions


def test_assert_no_untested_objs() -> None:
    """Test func for _assert_no_untested_objs."""
    # Test with a test function - should not raise (functions have no sub-objects)
    assert_no_untested_objs(test_assert_no_untested_objs)

    # Test with a real test module that we know has complete coverage
    # Use the test_assertions module which should have complete coverage
    # This should not raise since test_assertions should have complete coverage
    assert_no_untested_objs(test_assertions)
