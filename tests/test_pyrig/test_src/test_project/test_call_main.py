"""Test module."""

from pytest_mock import MockFixture

from pyrig import main
from pyrig.src.project.call_main import call_main


def test_call_main(mocker: MockFixture) -> None:
    """Test func for call_main."""
    # just verify it runs without error

    mock_main = mocker.patch.object(main, main.main.__name__)

    call_main()

    mock_main.assert_called_once()
