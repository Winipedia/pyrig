"""module."""

from pathlib import Path

from pyrig.dev.configs.git.branch_protection import BranchProtectionConfigFile


class TestBranchProtectionConfigFile:
    """Test class."""

    def test_get_parent_path(self) -> None:
        """Test method."""
        assert BranchProtectionConfigFile.get_parent_path() == Path()

    def test_get_filename(self) -> None:
        """Test method."""
        assert BranchProtectionConfigFile.get_filename() == "branch-protection"

    def test__get_configs(self) -> None:
        """Test method."""
        configs = BranchProtectionConfigFile.get_configs()
        assert isinstance(configs, dict)
