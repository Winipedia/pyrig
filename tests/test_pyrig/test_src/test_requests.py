"""module."""

from pyrig.rig.tools.remote_version_controller import RemoteVersionController
from pyrig.src.requests import internet_is_available


def test_internet_is_available() -> None:
    """Test function."""
    assert isinstance(internet_is_available(), bool)

    if RemoteVersionController.I.running_in_ci():
        assert internet_is_available(), "Expected internet to be available in CI"
