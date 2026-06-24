"""Tests for RepoSettingsConfigFile."""

from pathlib import Path

from pyrig.rig.configs.version_control.remote.settings import (
    RepoSettingsConfigFile,
)


class TestRepoSettingsConfigFile:
    """Test class."""

    def test_repository_key(self) -> None:
        """Test method."""
        assert RepoSettingsConfigFile.I.repository_key() == "repository"

    def test_rulesets_key(self) -> None:
        """Test method."""
        assert RepoSettingsConfigFile.I.rulesets_key() == "rulesets"

    def test_parent_path(self) -> None:
        """Test method."""
        assert RepoSettingsConfigFile.I.parent_path() == Path(".github")

    def test_stem(self) -> None:
        """Test method."""
        assert RepoSettingsConfigFile.I.stem() == "settings"

    def test__configs(self) -> None:
        """Test method."""
        configs = RepoSettingsConfigFile.I.configs()
        assert isinstance(configs, dict)
        assert RepoSettingsConfigFile.I.repository_key() in configs
        assert RepoSettingsConfigFile.I.rulesets_key() in configs
        assert isinstance(configs[RepoSettingsConfigFile.I.rulesets_key()], list)
