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

    def test_fork_pr_contributor_approval_key(self) -> None:
        """Test method."""
        assert (
            RepositorySettingsConfigFile.I.fork_pr_contributor_approval_key()
            == "fork_pr_contributor_approval"
        )

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
        assert (
            RepositorySettingsConfigFile.I.fork_pr_contributor_approval_key() in configs
        )

    def test_bypass_actors(self) -> None:
        """Test method."""
        actors = RepositorySettingsConfigFile.I.bypass_actors()
        assert actors == [
            RepositorySettingsConfigFile.I.admin_bypass_actor(),
        ]

    def test_admin_bypass_actor(self) -> None:
        """Test method."""
        assert RepositorySettingsConfigFile.I.admin_bypass_actor() == {
            "actor_id": 5,
            "actor_type": "RepositoryRole",
            "bypass_mode": "always",
        }

    def test_required_status_checks(self) -> None:
        """Test method."""
        assert RepositorySettingsConfigFile.I.required_status_checks() == [
            RepositorySettingsConfigFile.I.status_check_health_check(),
        ]

    def test_status_check_health_check(self) -> None:
        """Test method."""
        assert RepositorySettingsConfigFile.I.status_check_health_check() == {
            "context": "Health Check / Health Check",
            "integration_id": 15368,
        }

    def test_github_actions_status_check(self) -> None:
        """Test method."""
        assert RepositorySettingsConfigFile.I.github_actions_status_check(
            workflow="Build",
            job="Test",
        ) == {
            "context": "Build / Test",
            "integration_id": 15368,
        }

    def test_status_check(self) -> None:
        """Test method."""
        assert RepositorySettingsConfigFile.I.status_check(
            workflow="Build",
            job="Test",
            integration_id=42,
        ) == {
            "context": "Build / Test",
            "integration_id": 42,
        }
