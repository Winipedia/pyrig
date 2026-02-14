"""module."""

import pyrig
from pyrig.rig import configs
from pyrig.rig.configs.base.base import ConfigFile
from pyrig.rig.configs.git.gitignore import GitignoreConfigFile
from pyrig.rig.tests.mirror_test import MirrorTestConfigFile
from pyrig.src.subclass import DependencySubclass


class TestDependencySubclass:
    """Test class."""

    def test_I(self) -> None:  # noqa: N802
        """Test method."""
        result = GitignoreConfigFile.I
        assert isinstance(result, GitignoreConfigFile)
        assert result is GitignoreConfigFile.I.I
        assert result is GitignoreConfigFile.L()

    def test_definition_package(self) -> None:
        """Test method."""
        result = ConfigFile.definition_package()
        assert issubclass(ConfigFile, DependencySubclass)
        assert result == configs

    def test_sorting_key(self) -> None:
        """Test method."""
        result = ConfigFile.sorting_key(ConfigFile)
        assert isinstance(result, (float, int))

    def test_base_dependency(self) -> None:
        """Test method."""
        result = ConfigFile.base_dependency()
        assert result == pyrig

    def test_subclasses(self) -> None:
        """Test method."""
        result = ConfigFile.subclasses()
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(issubclass(subclass, ConfigFile) for subclass in result)

    def test_L(self) -> None:  # noqa: N802
        """Test method."""
        assert MirrorTestConfigFile.L.L is MirrorTestConfigFile


class TestSingletonDependencySubclass:
    """Test class."""
