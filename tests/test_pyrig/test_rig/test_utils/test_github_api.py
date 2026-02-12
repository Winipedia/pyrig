"""test module."""

from github.Repository import Repository

from pyrig.rig.configs.git.branch_protection import RepoProtectionConfigFile
from pyrig.rig.tools.version_controller import VersionController
from pyrig.rig.utils.github_api import (
    create_or_update_ruleset,
    get_all_rulesets,
    get_repo,
    github_api_request,
    ruleset_exists,
)
from pyrig.rig.utils.testing import skip_if_no_internet
from pyrig.rig.utils.version_control import (
    get_github_repo_token,
)


@skip_if_no_internet
def test_get_repo() -> None:
    """Test function."""
    owner, repo_name = VersionController.L.get_repo_owner_and_name()
    repo = get_repo(
        get_github_repo_token(),
        owner,
        repo_name,
    )
    assert isinstance(repo, Repository), "Expected Repository object"
    assert repo.name == repo_name, f"Expected repo name {repo_name}, got {repo.name}"


@skip_if_no_internet
def test_get_all_rulesets() -> None:
    """Test function."""
    rulesets = get_all_rulesets(
        get_github_repo_token(),
        *VersionController.L.get_repo_owner_and_name(),
    )
    assert isinstance(rulesets, list), "Expected rulesets to be a list"


@skip_if_no_internet
def test_ruleset_exists() -> None:
    """Test function."""
    owner, repo_name = VersionController.L.get_repo_owner_and_name()
    ruleset_id = ruleset_exists(
        get_github_repo_token(),
        owner,
        repo_name,
        VersionController.L.get_default_ruleset_name(),
    )
    assert ruleset_id > 0, f"Expected ruleset id > 0, got {ruleset_id}"


@skip_if_no_internet
def test_create_or_update_ruleset() -> None:
    """Test function."""
    token = get_github_repo_token()
    owner, repo_name = VersionController.L.get_repo_owner_and_name()
    create_or_update_ruleset(
        token=token,
        owner=owner,
        repo_name=repo_name,
        **RepoProtectionConfigFile.load(),
    )


@skip_if_no_internet
def test_github_api_request() -> None:
    """Test function."""
    owner, repo_name = VersionController.L.get_repo_owner_and_name()
    github_api_request(
        get_github_repo_token(),
        owner,
        repo_name,
        "rulesets",
        method="GET",
    )
