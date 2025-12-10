"""module."""

from pyrig.dev.cli.commands.protect_repo import (
    create_or_update_default_branch_ruleset,
    get_default_ruleset_params,
    protect_repository,
    set_secure_repo_settings,
)
from pyrig.src.testing.assertions import assert_with_msg


def test_protect_repository() -> None:
    """Test func for protect_repository."""
    protect_repository()


def test_set_secure_repo_settings() -> None:
    """Test func for set_secure_repo_settings."""
    set_secure_repo_settings()


def test_create_or_update_default_branch_ruleset() -> None:
    """Test func for create_or_update_default_branch_ruleset."""
    create_or_update_default_branch_ruleset()


def test_get_default_ruleset_params() -> None:
    """Test func for get_default_ruleset_params."""
    params = get_default_ruleset_params()
    assert_with_msg(
        "owner" in params,
        "Expected 'owner' in params",
    )
    assert_with_msg(
        "token" in params,
        "Expected 'token' in params",
    )
