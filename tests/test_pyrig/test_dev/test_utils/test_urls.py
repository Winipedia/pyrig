"""test module."""

from pyrig.dev.utils.urls import (
    get_codecov_url,
    get_github_pages_url,
    get_github_repo_url,
    get_github_workflow_badge_url,
    get_github_workflow_run_url,
    get_licence_badge_url,
    get_pypi_badge_url,
    get_pypi_url,
)


def test_get_github_repo_url() -> None:
    """Test function."""
    url = get_github_repo_url()
    assert isinstance(url, str), f"Expected url to be str, got {type(url)}"
    assert "github.com" in url, f"Expected 'github.com' in url, got {url}"


def test_get_github_pages_url() -> None:
    """Test function."""
    url = get_github_pages_url()
    assert isinstance(url, str), f"Expected url to be str, got {type(url)}"
    assert "github.io" in url, f"Expected 'github.io' in url, got {url}"


def test_get_codecov_url() -> None:
    """Test function."""
    url = get_codecov_url()
    assert isinstance(url, str), f"Expected url to be str, got {type(url)}"
    assert "codecov.io" in url, f"Expected 'codecov.io' in url, got {url}"


def test_get_pypi_url() -> None:
    """Test function."""
    url = get_pypi_url()
    assert isinstance(url, str), f"Expected url to be str, got {type(url)}"
    assert "pypi.org" in url, f"Expected 'pypi.org' in url, got {url}"


def test_get_pypi_badge_url() -> None:
    """Test function."""
    url = get_pypi_badge_url()
    assert isinstance(url, str), f"Expected url to be str, got {type(url)}"
    assert "img.shields.io" in url, f"Expected 'img.shields.io' in url, got {url}"


def test_get_github_workflow_run_url() -> None:
    """Test function."""
    url = get_github_workflow_run_url("build")
    assert isinstance(url, str), f"Expected url to be str, got {type(url)}"
    assert "github.com" in url, f"Expected 'github.com' in url, got {url}"


def test_get_github_workflow_badge_url() -> None:
    """Test function."""
    url = get_github_workflow_badge_url("build", "CI", "github")
    assert isinstance(url, str), f"Expected url to be str, got {type(url)}"
    assert "img.shields.io" in url, f"Expected 'img.shields.io' in url, got {url}"


def test_get_licence_badge_url() -> None:
    """Test function."""
    url = get_licence_badge_url()
    assert isinstance(url, str), f"Expected url to be str, got {type(url)}"
    assert "img.shields.io" in url, f"Expected 'img.shields.io' in url, got {url}"
