"""tests for pyrig.src.git module."""

import os

from pyrig.src.git import (
    running_in_github_actions,
)


def test_running_in_github_actions() -> None:
    """Test func for running_in_github_actions."""
    is_running_og = running_in_github_actions()
    assert isinstance(is_running_og, bool), (
        f"Expected is_running to be bool, got {type(is_running_og)}"
    )

    # set env var to true and check again
    os.environ["GITHUB_ACTIONS"] = "true"
    is_running = running_in_github_actions()
    assert is_running, "Expected is_running to be True when env var set to true"

    # set to false and check again
    os.environ["GITHUB_ACTIONS"] = "false"
    is_running = running_in_github_actions()
    assert not is_running, "Expected is_running to be False when env var set to false"

    # set back to original
    os.environ["GITHUB_ACTIONS"] = "true" if is_running_og else "false"
    assert running_in_github_actions() == is_running_og, (
        "Expected is_running to be original value after reset"
    )
