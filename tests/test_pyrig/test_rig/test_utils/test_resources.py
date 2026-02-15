"""module."""

from pathlib import Path

from pytest_mock import MockFixture
from requests import RequestException

from pyrig.rig.configs.license import LicenseConfigFile
from pyrig.rig.utils import resources
from pyrig.rig.utils.packages import src_package_is_pyrig
from pyrig.rig.utils.resources import (
    requests_get_text_cached,
    return_resource_content_on_fetch_error,
    return_resource_file_content_on_exceptions_or_in_dep,
)
from pyrig.rig.utils.testing import skip_if_no_internet
from pyrig.src.resource import resource_path


def test_return_resource_file_content_on_exceptions_or_in_dep(
    tmp_path: Path, mocker: MockFixture
) -> None:
    """Test function."""
    # mock pyrig.resources.resource_path to return tmp_path / "test_resource.txt"
    path = tmp_path / "test_resource.txt"

    mocker.patch(
        resources.__name__ + "." + resource_path.__name__,
        return_value=path,
    )
    # create resource file
    path.write_text("Hello World!")

    @return_resource_file_content_on_exceptions_or_in_dep(
        "test_resource.txt", (ValueError,)
    )
    def test_func() -> str:
        msg = "Test exception"
        raise ValueError(msg)

    # now test_func should return "Hello World!" instead of raising ValueError
    assert test_func() == "Hello World!"


@skip_if_no_internet
def test_return_resource_content_on_fetch_error(
    tmp_path: Path, mocker: MockFixture
) -> None:
    """Test function."""
    # mock pyrig.resources.resource_path to return tmp_path / "test_resource.txt"
    path = tmp_path / "test_resource.txt"
    mocker.patch(
        resources.__name__ + "." + resource_path.__name__,
        return_value=path,
    )
    # create resource file
    path.write_text("Hello World!")

    @return_resource_content_on_fetch_error("test_resource.txt")
    def test_func() -> str:
        msg = "Test exception"
        raise RequestException(msg)

    # now test_func should return "Hello World!" instead of raising ValueError
    assert test_func() == "Hello World!"

    # patch src_package_is_pyrig to return False
    mock = mocker.patch(
        resources.__name__ + "." + src_package_is_pyrig.__name__, return_value=False
    )
    request_get_mock = mocker.patch("requests.get")
    # now call a func that uses the decorator without raising an exception
    # - should return resource content directly
    LicenseConfigFile().mit_license()
    # should not have called requests.get
    request_get_mock.assert_not_called()
    # should have called src_package_is_pyrig
    mock.assert_called_once()


def test_requests_get_text_cached() -> None:
    """Test function."""
    response_text = requests_get_text_cached("https://httpbin.org/get")
    assert isinstance(response_text, str)
    assert len(response_text) > 0
