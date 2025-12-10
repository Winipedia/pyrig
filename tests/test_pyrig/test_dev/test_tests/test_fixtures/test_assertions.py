"""module."""

from collections.abc import Callable


def test_main_test_fixture(main_test_fixture: None) -> None:
    """Test function."""
    assert main_test_fixture is None


def test_assert_no_untested_objs(
    assert_no_untested_objs: Callable[[object], None],
) -> None:
    """Test function."""
    assert_no_untested_objs(test_assert_no_untested_objs)
