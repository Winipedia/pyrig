"""module."""

from pyrig.src.git import running_in_github_actions
from pyrig.src.requests import internet_is_available


def test_internet_is_available() -> None:
    """Test function."""
    assert isinstance(internet_is_available(), bool)

    if running_in_github_actions():
        assert internet_is_available(), "Expected internet to be available in CI"
