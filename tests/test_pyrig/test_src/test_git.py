"""tests for pyrig.src.git module."""

from pathlib import Path

import pyrig
from pyrig.src.git import (
    get_codecov_url_from_git,
    get_git_unstaged_changes,
    get_git_username,
    get_github_pages_url_from_git,
    get_licence_badge_url_from_git,
    get_pypi_badge_url_from_git,
    get_pypi_url_from_git,
    get_repo_owner_and_name_from_git,
    get_repo_remote_from_git,
    get_repo_url_from_git,
    get_workflow_badge_url_from_git,
    get_workflow_run_url_from_git,
    git_add_file,
)
from pyrig.src.testing.assertions import assert_with_msg


def test_get_repo_remote_from_git() -> None:
    """Test func for get_repo_url_from_git."""
    url = get_repo_remote_from_git()
    assert_with_msg(isinstance(url, str), f"Expected url to be str, got {type(url)}")

    assert_with_msg("github.com" in url, f"Expected 'github.com' in url, got {url}")


def test_get_repo_owner_and_name_from_git() -> None:
    """Test func for get_repo_owner_and_name_from_git."""
    owner, repo = get_repo_owner_and_name_from_git()
    assert_with_msg(
        isinstance(owner, str), f"Expected owner to be str, got {type(owner)}"
    )

    assert owner == "Winipedia", f"Expected owner to be 'Winipedia', got {owner}"
    assert repo == pyrig.__name__, f"Expected repo to be 'pyrig', got {repo}"


def test_get_git_username() -> None:
    """Test function."""
    username = get_git_username()
    assert isinstance(username, str), (
        f"Expected username to be str, got {type(username)}"
    )
    assert len(username) > 0, "Expected username to be non-empty"


def test_get_git_unstaged_changes() -> None:
    """Test function."""
    assert isinstance(get_git_unstaged_changes(), str), (
        "Expected get_git_unstaged_changes to return str"
    )


def test_git_add_file() -> None:
    """Test function."""
    no_file = Path("non_existent_file.txt")
    assert not no_file.exists(), "Expected file not to exist"
    completed_process = git_add_file(no_file, check=False)
    stderr = completed_process.stderr.decode("utf-8")
    assert "fatal: pathspec 'non_existent_file.txt' did not match any files" in stderr
    assert not no_file.exists(), "Expected file not to exist after git add"


def test_get_repo_url_from_git() -> None:
    """Test function."""
    url = get_repo_url_from_git()
    assert isinstance(url, str), f"Expected url to be str, got {type(url)}"
    assert "github.com" in url, f"Expected 'github.com' in url, got {url}"


def test_get_github_pages_url_from_git() -> None:
    """Test function."""
    url = get_github_pages_url_from_git()
    assert isinstance(url, str), f"Expected url to be str, got {type(url)}"
    assert "github.io" in url, f"Expected 'github.io' in url, got {url}"


def test_get_codecov_url_from_git() -> None:
    """Test function."""
    url = get_codecov_url_from_git()
    assert isinstance(url, str), f"Expected url to be str, got {type(url)}"
    assert "codecov.io" in url, f"Expected 'codecov.io' in url, got {url}"


def test_get_pypi_url_from_git() -> None:
    """Test function."""
    url = get_pypi_url_from_git()
    assert isinstance(url, str), f"Expected url to be str, got {type(url)}"
    assert "pypi.org" in url, f"Expected 'pypi.org' in url, got {url}"


def test_get_pypi_badge_url_from_git() -> None:
    """Test function."""
    url = get_pypi_badge_url_from_git()
    assert isinstance(url, str), f"Expected url to be str, got {type(url)}"
    assert "img.shields.io" in url, f"Expected 'img.shields.io' in url, got {url}"


def test_get_workflow_run_url_from_git() -> None:
    """Test function."""
    url = get_workflow_run_url_from_git("build")
    assert isinstance(url, str), f"Expected url to be str, got {type(url)}"
    assert "github.com" in url, f"Expected 'github.com' in url, got {url}"


def test_get_workflow_badge_url_from_git() -> None:
    """Test function."""
    url = get_workflow_badge_url_from_git("build", "CI", "github")
    assert isinstance(url, str), f"Expected url to be str, got {type(url)}"
    assert "img.shields.io" in url, f"Expected 'img.shields.io' in url, got {url}"


def test_get_licence_badge_url_from_git() -> None:
    """Test function."""
    url = get_licence_badge_url_from_git()
    assert isinstance(url, str), f"Expected url to be str, got {type(url)}"
    assert "img.shields.io" in url, f"Expected 'img.shields.io' in url, got {url}"
