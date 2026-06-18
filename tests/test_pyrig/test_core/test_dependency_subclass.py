"""module."""

import inspect

import pytest
from pyrig_dev.rig.configs.pyproject import PyprojectConfigFile

from pyrig import rig
from pyrig.core.dependency_subclass import DependencySubclass
from pyrig.rig import configs
from pyrig.rig.configs.base.config_file import ConfigFile
from pyrig.rig.configs.license import LicenseConfigFile
from pyrig.rig.configs.version_control.ignore import (
    VersionControllerIgnoreConfigFile,
)
from pyrig.rig.tests.mirror_test import MirrorTestConfigFile
from pyrig.rig.tools.base.tool import Tool
from pyrig.rig.tools.programming_language import ProgrammingLanguage


class TestDependencySubclass:
    """Test class."""

    def test_leaf(self) -> None:
        """Test method."""
        leaf = ProgrammingLanguage.leaf()
        assert issubclass(leaf, ProgrammingLanguage)
        assert ProgrammingLanguage.leaf() is ProgrammingLanguage.leaf().leaf()

        with pytest.raises(
            RuntimeError, match=r"Multiple leaf subclasses found for .*."
        ):
            _ = Tool.leaf()

    def test___str__(self) -> None:
        """Test method."""
        assert isinstance(str(ConfigFile), str)

    def test_concrete_subclasses(self) -> None:
        """Test method."""
        result = tuple(ConfigFile.concrete_subclasses())
        assert len(result) > 0
        assert all(issubclass(subclass, ConfigFile) for subclass in result)
        assert all(not inspect.isabstract(subclass) for subclass in result)

    def test_subclasses_sorted(self) -> None:
        """Test method."""
        subclasses = (
            PyprojectConfigFile,
            LicenseConfigFile,
        )
        result = ConfigFile.subclasses_sorted(subclasses)
        assert result == [
            LicenseConfigFile,
            PyprojectConfigFile,
        ]

    def test_I(self) -> None:  # noqa: N802
        """Test method."""
        result = VersionControllerIgnoreConfigFile.I
        assert isinstance(result, VersionControllerIgnoreConfigFile)
        assert result is VersionControllerIgnoreConfigFile.I.I

    def test_dependency_package(self) -> None:
        """Test method."""
        result = ConfigFile.dependency_package()
        assert issubclass(ConfigFile, DependencySubclass)
        assert result == configs
        assert DependencySubclass.dependency_package() is rig

    def test_sort_key(self) -> None:
        """Test method."""
        result = PyprojectConfigFile.sort_key()
        assert isinstance(result, (float, int))

        assert DependencySubclass.sort_key() == DependencySubclass.__name__

    def test_subclasses(self) -> None:
        """Test method."""
        result = tuple(ConfigFile.subclasses())
        assert len(result) > 0
        assert all(issubclass(subclass, ConfigFile) for subclass in result)

    def test_L(self) -> None:  # noqa: N802
        """Test method."""
        assert MirrorTestConfigFile.L.L.L is MirrorTestConfigFile.L
