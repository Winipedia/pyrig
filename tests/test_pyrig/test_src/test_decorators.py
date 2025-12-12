"""module."""

from pathlib import Path

from pytest_mock import MockFixture
from requests import RequestException

from pyrig.src import decorators
from pyrig.src.decorators import (
    return_resource_content_on_fetch_error,
    return_resource_file_content_on_exceptions,
)
from pyrig.src.resource import get_resource_path


def test_return_resource_file_content_on_exceptions(
    tmp_path: Path, mocker: MockFixture
) -> None:
    """Test function."""
    # mock pyrig.resources.get_resource_path to return tmp_path / "test_resource.txt"
    resource_path = tmp_path / "test_resource.txt"

    mocker.patch(
        decorators.__name__ + "." + get_resource_path.__name__,
        return_value=resource_path,
    )
    # create resource file
    resource_path.write_text("Hello World!")

    @return_resource_file_content_on_exceptions("test_resource.txt", (ValueError,))
    def test_func() -> str:
        msg = "Test exception"
        raise ValueError(msg)

    # now test_func should return "Hello World!" instead of raising ValueError
    assert test_func() == "Hello World!"


def test_return_resource_content_on_fetch_error(
    tmp_path: Path, mocker: MockFixture
) -> None:
    """Test function."""
    # mock pyrig.resources.get_resource_path to return tmp_path / "test_resource.txt"
    resource_path = tmp_path / "test_resource.txt"
    mocker.patch(
        decorators.__name__ + "." + get_resource_path.__name__,
        return_value=resource_path,
    )
    # create resource file
    resource_path.write_text("Hello World!")

    @return_resource_content_on_fetch_error("test_resource.txt")
    def test_func() -> str:
        msg = "Test exception"
        raise RequestException(msg)

    # now test_func should return "Hello World!" instead of raising ValueError
    assert test_func() == "Hello World!"
