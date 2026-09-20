"""Tests for DependencyBotConfigFile."""

from pathlib import Path

from pyrig.rig.configs.version_control.remote.dependency_bot import (
    DependencyBotConfigFile,
)


class TestDependencyBotConfigFile:
    """Test class."""

    def test_parent_path(self) -> None:
        """Test method."""
        assert DependencyBotConfigFile.I.parent_path() == Path(".github")

    def test_stem(self) -> None:
        """Test method."""
        assert DependencyBotConfigFile.I.stem() == "dependabot"

    def test_ecosystem_config(self) -> None:
        """Test method."""
        assert DependencyBotConfigFile.I.ecosystem_config("example") == {
            "package-ecosystem": "example",
            "directory": "/",
            "schedule": {"interval": "weekly"},
            "cooldown": {"default-days": 7},
        }

        assert DependencyBotConfigFile.I.ecosystem_config(
            "example",
            directory="/nested",
            schedule={"interval": "daily"},
            cooldown={"default-days": 14},
        ) == {
            "package-ecosystem": "example",
            "directory": "/nested",
            "schedule": {"interval": "daily"},
            "cooldown": {"default-days": 14},
        }

    def test__configs(self) -> None:
        """Test method."""
        configs = DependencyBotConfigFile.I.configs()
        assert configs == {
            "version": 2,
            "updates": [
                {
                    "package-ecosystem": "uv",
                    "directory": "/",
                    "schedule": {"interval": "weekly"},
                    "cooldown": {"default-days": 7},
                },
                {
                    "package-ecosystem": "github-actions",
                    "directory": "/",
                    "schedule": {"interval": "weekly"},
                    "cooldown": {"default-days": 7},
                },
            ],
        }
