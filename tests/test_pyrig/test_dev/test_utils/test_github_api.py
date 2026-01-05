"""test module."""

from github.Repository import Repository

from pyrig.dev.cli.commands.protect_repo import get_default_ruleset_params
from pyrig.dev.utils.github_api import (
    create_or_update_ruleset,
    get_all_rulesets,
    get_repo,
    github_api_request,
    ruleset_exists,
)
from pyrig.dev.utils.version_control import (
    DEFAULT_RULESET_NAME,
    get_github_repo_token,
    get_repo_owner_and_name_from_version_control,
)


def test_get_repo() -> None:
    """Test func for get_repo."""
    owner, repo_name = get_repo_owner_and_name_from_version_control()
    repo = get_repo(
        get_github_repo_token(),
        owner,
        repo_name,
    )
    assert isinstance(repo, Repository), "Expected Repository object"
    assert repo.name == repo_name, f"Expected repo name {repo_name}, got {repo.name}"


def test_get_all_rulesets() -> None:
    """Test func for get_all_rulesets."""
    rulesets = get_all_rulesets(
        get_github_repo_token(),
        *get_repo_owner_and_name_from_version_control(),
    )
    assert isinstance(rulesets, list), "Expected rulesets to be a list"


def test_ruleset_exists() -> None:
    """Test func for ruleset_exists."""
    ruleset_id = ruleset_exists(
        get_github_repo_token(),
        *get_repo_owner_and_name_from_version_control(),
        DEFAULT_RULESET_NAME,
    )
    assert ruleset_id > 0, f"Expected ruleset id > 0, got {ruleset_id}"


def test_create_or_update_ruleset() -> None:
    """Test func for create_or_update_ruleset."""
    token = get_github_repo_token()
    owner, repo_name = get_repo_owner_and_name_from_version_control()
    create_or_update_ruleset(
        token=token,
        owner=owner,
        repo_name=repo_name,
        **get_default_ruleset_params(),
    )


def test_github_api_request() -> None:
    """Test function."""
    github_api_request(
        get_github_repo_token(),
        *get_repo_owner_and_name_from_version_control(),
        "rulesets",
        method="GET",
    )
