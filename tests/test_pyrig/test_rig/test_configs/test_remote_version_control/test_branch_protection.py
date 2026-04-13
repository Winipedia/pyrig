"""module."""

from pathlib import Path

from pyrig.rig.configs.remote_version_control.branch_protection import (
    BranchProtectionConfigFile,
)


class TestBranchProtectionConfigFile:
    """Test class."""

    def test_repo_token(self) -> None:
        """Test method."""
        token = BranchProtectionConfigFile.I.repo_token()
        assert isinstance(token, str), f"Expected token to be str, got {type(token)}"

    def test_protect_repo(self) -> None:
        """Test method."""
        BranchProtectionConfigFile.I.protect_repo()

    def test_create_or_update_default_branch_ruleset(self) -> None:
        """Test method."""
        BranchProtectionConfigFile.I.create_or_update_default_branch_ruleset()

    def test_set_secure_repo_settings(self) -> None:
        """Test method."""
        BranchProtectionConfigFile.I.set_secure_repo_settings()

    def test_parent_path(self) -> None:
        """Test method."""
        assert BranchProtectionConfigFile.I.parent_path() == Path()

    def test_stem(self) -> None:
        """Test method."""
        assert BranchProtectionConfigFile.I.stem() == "branch-protection"

    def test__configs(self) -> None:
        """Test method."""
        configs = BranchProtectionConfigFile.I.configs()
        assert isinstance(configs, dict)
