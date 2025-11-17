"""tests for py_dev.utils.git.github.github module."""

import os

from py_dev.utils.git.github.github import (
    get_github_repo_token,
    running_in_github_actions,
)
from py_dev.utils.testing.assertions import assert_with_msg


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
