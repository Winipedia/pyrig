"""Tests for RepositorySettingsConfigFile."""

from pathlib import Path

from pyrig.rig.configs.version_control.remote.settings import (
    RepositorySettingsConfigFile,
)


class TestRepositorySettingsConfigFile:
    """Test class."""

    def test_repository_key(self) -> None:
        """Test method."""
        assert RepositorySettingsConfigFile.I.repository_key() == "repository"

    def test_rulesets_key(self) -> None:
        """Test method."""
        assert RepositorySettingsConfigFile.I.rulesets_key() == "rulesets"

    def test_parent_path(self) -> None:
        """Test method."""
        assert RepositorySettingsConfigFile.I.parent_path() == Path(".github")

    def test_stem(self) -> None:
        """Test method."""
        assert RepositorySettingsConfigFile.I.stem() == "settings"

    def test__configs(self) -> None:
        """Test method."""
        configs = RepositorySettingsConfigFile.I.configs()
        assert isinstance(configs, dict)
        assert RepositorySettingsConfigFile.I.repository_key() in configs
        assert RepositorySettingsConfigFile.I.rulesets_key() in configs
        assert isinstance(configs[RepositorySettingsConfigFile.I.rulesets_key()], list)
