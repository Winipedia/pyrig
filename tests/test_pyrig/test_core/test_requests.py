"""module."""

from pytest_mock import MockerFixture

from pyrig.core.requests import internet_is_available
from pyrig.rig.tools.version_control.remote import (
    RemoteVersionController,
)


def test_internet_is_available(mocker: MockerFixture) -> None:
    """Test function."""
    assert isinstance(internet_is_available(), bool)

    if RemoteVersionController.I.running_in_ci():
        assert internet_is_available(), "Expected internet to be available in CI"

    # mocking socket.create_connection to simulate no internet connectivity
    mock_create_connection = mocker.patch(
        "socket.create_connection", side_effect=OSError("No internet connectivity")
    )
    assert not internet_is_available()
    mock_create_connection.assert_called_once()
