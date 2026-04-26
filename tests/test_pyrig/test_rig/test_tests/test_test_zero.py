"""Test module."""

from pyrig.core.introspection.modules import module_content
from pyrig.rig.tests import test_zero as test_zero_module
from pyrig.rig.tests.test_zero import test_zero


def test_test_zero() -> None:
    """Test function."""
    assert test_zero() is None

    content = module_content(test_zero_module)

    assert (
        content
        == '''"""Contains an empty test.

This test exists so that when no tests are written yet pytest runs successfully
and does not fail because no tests are found and to execute the autouse fixtures.
"""


def test_zero() -> None:
    """Empty test."""
'''
    )
