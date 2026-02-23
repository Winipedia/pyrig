"""module."""

import pyrig
from pyrig.rig import configs
from pyrig.rig.configs.base.base import ConfigFile
from pyrig.rig.configs.git.gitignore import GitignoreConfigFile
from pyrig.rig.configs.license import LicenseConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.tests.mirror_test import MirrorTestConfigFile
from pyrig.src.subclass import DependencySubclass


class TestDependencySubclass:
    """Test class."""

    def test_subclasses_sorted(self) -> None:
        """Test method."""
        subclasses = (PyprojectConfigFile, LicenseConfigFile, GitignoreConfigFile)
        result = ConfigFile.subclasses_sorted(*subclasses)
        assert result == [LicenseConfigFile, PyprojectConfigFile, GitignoreConfigFile]

    def test_I(self) -> None:  # noqa: N802
        """Test method."""
        result = GitignoreConfigFile.I
        assert isinstance(result, GitignoreConfigFile)
        assert result is GitignoreConfigFile.I.I

    def test_definition_package(self) -> None:
        """Test method."""
        result = ConfigFile.definition_package()
        assert issubclass(ConfigFile, DependencySubclass)
        assert result == configs

    def test_sorting_key(self) -> None:
        """Test method."""
        result = ConfigFile.sorting_key(PyprojectConfigFile)
        assert isinstance(result, (float, int))

    def test_base_dependency(self) -> None:
        """Test method."""
        result = ConfigFile.base_dependency()
        assert result == pyrig

    def test_subclasses(self) -> None:
        """Test method."""
        result = tuple(ConfigFile.subclasses())
        assert len(result) > 0
        assert all(issubclass(subclass, ConfigFile) for subclass in result)

    def test_L(self) -> None:  # noqa: N802
        """Test method."""
        assert MirrorTestConfigFile.I.L.L is MirrorTestConfigFile
