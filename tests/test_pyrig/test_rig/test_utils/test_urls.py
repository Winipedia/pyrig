"""test module."""

from pyrig.rig.utils.urls import (
    get_codecov_url,
    get_pypi_badge_url,
    get_pypi_url,
)


def test_get_codecov_url() -> None:
    """Test function."""
    url = get_codecov_url()
    assert isinstance(url, str), f"Expected url to be str, got {type(url)}"


def test_get_pypi_url() -> None:
    """Test function."""
    url = get_pypi_url()
    assert isinstance(url, str), f"Expected url to be str, got {type(url)}"


def test_get_pypi_badge_url() -> None:
    """Test function."""
    url = get_pypi_badge_url()
    assert isinstance(url, str), f"Expected url to be str, got {type(url)}"
