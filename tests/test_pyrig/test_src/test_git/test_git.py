"""tests for pyrig.src.git.github.github module."""

import os
from pathlib import Path

import pyrig
from pyrig.src.git.git import (
    get_git_unstaged_changes,
    get_git_username,
    get_github_repo_token,
    get_repo_owner_and_name_from_git,
    get_repo_url_from_git,
    git_add_file,
    running_in_github_actions,
)
from pyrig.src.testing.assertions import assert_with_msg


def test_get_github_repo_token() -> None:
    """Test func for get_github_token."""
    token = get_github_repo_token()
    assert_with_msg(
        isinstance(token, str), f"Expected token to be str, got {type(token)}"
    )


def test_running_in_github_actions() -> None:
    """Test func for running_in_github_actions."""
    is_running_og = running_in_github_actions()
    assert_with_msg(
        isinstance(is_running_og, bool),
        f"Expected is_running to be bool, got {type(is_running_og)}",
    )

    # set env var to true and check again
    os.environ["GITHUB_ACTIONS"] = "true"
    is_running = running_in_github_actions()
    assert_with_msg(
        is_running, "Expected is_running to be True when env var set to true"
    )

    # set to false and check again
    os.environ["GITHUB_ACTIONS"] = "false"
    is_running = running_in_github_actions()
    assert_with_msg(
        not is_running, "Expected is_running to be False when env var set to false"
    )

    # set back to original
    os.environ["GITHUB_ACTIONS"] = "true" if is_running_og else "false"
    assert_with_msg(
        running_in_github_actions() == is_running_og,
        "Expected is_running to be original value after reset",
    )


def test_get_repo_url_from_git() -> None:
    """Test func for get_repo_url_from_git."""
    url = get_repo_url_from_git()
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
