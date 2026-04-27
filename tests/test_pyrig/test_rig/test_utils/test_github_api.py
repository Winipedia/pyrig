"""test module."""

from github.Repository import Repository

from pyrig.rig.configs.remote_version_control.branch_protection import (
    BranchProtectionConfigFile,
)
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.version_control.version_controller import VersionController
from pyrig.rig.utils.github_api import (
    all_rulesets,
    create_or_update_ruleset,
    github_api_request,
    repository,
    ruleset_exists,
)


def test_repository() -> None:
    """Test function."""
    owner, repo_name = VersionController.I.repo_owner(), PackageManager.I.project_name()
    repo = repository(
        BranchProtectionConfigFile.I.repo_token(),
        owner,
        repo_name,
    )
    assert isinstance(repo, Repository), "Expected Repository object"
    assert repo.name == repo_name, f"Expected repo name {repo_name}, got {repo.name}"


def test_all_rulesets() -> None:
    """Test function."""
    rulesets = all_rulesets(
        BranchProtectionConfigFile.I.repo_token(),
        VersionController.I.repo_owner(),
        PackageManager.I.project_name(),
    )
    assert isinstance(rulesets, list), "Expected rulesets to be a list"


def test_ruleset_exists() -> None:
    """Test function."""
    owner, repo_name = VersionController.I.repo_owner(), PackageManager.I.project_name()
    ruleset_id = ruleset_exists(
        BranchProtectionConfigFile.I.repo_token(),
        owner,
        repo_name,
        VersionController.I.default_ruleset_name(),
    )
    assert ruleset_id > 0, f"Expected ruleset id > 0, got {ruleset_id}"


def test_create_or_update_ruleset() -> None:
    """Test function."""
    token = BranchProtectionConfigFile.I.repo_token()
    owner, repo_name = VersionController.I.repo_owner(), PackageManager.I.project_name()
    create_or_update_ruleset(
        token=token,
        owner=owner,
        repo_name=repo_name,
        **BranchProtectionConfigFile.I.load()[0],
    )


def test_github_api_request() -> None:
    """Test function."""
    owner, repo_name = VersionController.I.repo_owner(), PackageManager.I.project_name()
    github_api_request(
        BranchProtectionConfigFile.I.repo_token(),
        owner,
        repo_name,
        "rulesets",
        method="GET",
    )
