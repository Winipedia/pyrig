"""Test module."""

from pytest_mock import MockerFixture
from requests import Response

from pyrig.core.network import get, get_json, get_text

TEST_GET_URL = "https://pie.dev/get"


def test_get(mocker: MockerFixture) -> None:
    """Test function."""
    result = get(TEST_GET_URL)
    assert isinstance(result, Response)
    assert result.ok

    mock_get = mocker.patch(
        "pyrig.core.network.requests.get", return_value=mocker.Mock()
    )
    get(TEST_GET_URL)
    mock_get.assert_called_once_with(TEST_GET_URL, timeout=(3, 10))

    mock_get.reset_mock()
    get(TEST_GET_URL, timeout=5)
    mock_get.assert_called_once_with(TEST_GET_URL, timeout=5)


def test_get_text() -> None:
    """Test function."""
    result = get_text(TEST_GET_URL)
    assert f'"url": "{TEST_GET_URL}"' in result


def test_get_json() -> None:
    """Test function."""
    result = get_json(TEST_GET_URL)
    assert result["url"] == TEST_GET_URL
