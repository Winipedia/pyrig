"""module."""

from pyrig.rig.utils.version_control import (
    github_repo_token,
)


def test_github_repo_token() -> None:
    """Test function."""
    token = github_repo_token()
    assert isinstance(token, str), f"Expected token to be str, got {type(token)}"
