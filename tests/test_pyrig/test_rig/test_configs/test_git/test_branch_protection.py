"""module."""

from pathlib import Path

from pyrig.rig.configs.git.branch_protection import RepoProtectionConfigFile


class TestRepoProtectionConfigFile:
    """Test class."""

    def test_repo_token(self) -> None:
        """Test method."""
        token = RepoProtectionConfigFile.I.repo_token()
        assert isinstance(token, str), f"Expected token to be str, got {type(token)}"

    def test_protect_repo(self) -> None:
        """Test method."""
        RepoProtectionConfigFile.I.protect_repo()

    def test_create_or_update_default_branch_ruleset(self) -> None:
        """Test method."""
        RepoProtectionConfigFile.I.create_or_update_default_branch_ruleset()

    def test_set_secure_repo_settings(self) -> None:
        """Test method."""
        RepoProtectionConfigFile.I.set_secure_repo_settings()

    def test_parent_path(self) -> None:
        """Test method."""
        assert RepoProtectionConfigFile.I.parent_path() == Path()

    def test_stem(self) -> None:
        """Test method."""
        assert RepoProtectionConfigFile.I.stem() == "branch-protection"

    def test__configs(self) -> None:
        """Test method."""
        configs = RepoProtectionConfigFile.I.configs()
        assert isinstance(configs, dict)
