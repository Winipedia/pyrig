"""module."""

from pathlib import Path

from pyrig.rig.configs.git.branch_protection import RepoProtectionConfigFile
from pyrig.rig.utils.testing import skip_if_no_internet


class TestRepoProtectionConfigFile:
    """Test class."""

    @skip_if_no_internet
    def test_protect_repo(self) -> None:
        """Test method."""
        RepoProtectionConfigFile.L.protect_repo()

    @skip_if_no_internet
    def test_create_or_update_default_branch_ruleset(self) -> None:
        """Test method."""
        RepoProtectionConfigFile.L.create_or_update_default_branch_ruleset()

    @skip_if_no_internet
    def test_set_secure_repo_settings(self) -> None:
        """Test method."""
        RepoProtectionConfigFile.L.set_secure_repo_settings()

    def test_get_parent_path(self) -> None:
        """Test method."""
        assert RepoProtectionConfigFile.get_parent_path() == Path()

    def test_get_filename(self) -> None:
        """Test method."""
        assert RepoProtectionConfigFile.get_filename() == "branch-protection"

    def test__get_configs(self) -> None:
        """Test method."""
        configs = RepoProtectionConfigFile.get_configs()
        assert isinstance(configs, dict)
