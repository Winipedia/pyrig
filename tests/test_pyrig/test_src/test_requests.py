"""module."""

from pyrig.src.requests import internet_is_available


def test_internet_is_available() -> None:
    """Test function."""
    assert isinstance(internet_is_available(), bool)
