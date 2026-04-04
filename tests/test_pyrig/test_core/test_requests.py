"""module."""

from pyrig.core.requests import internet_is_available
from pyrig.rig.tools.remote_version_controller import RemoteVersionController


def test_internet_is_available() -> None:
    """Test function."""
    assert isinstance(internet_is_available(), bool)

    if RemoteVersionController.I.running_in_ci():
        assert internet_is_available(), "Expected internet to be available in CI"
