"""module."""

import inspect

import pytest

import pyrig
from pyrig.core.dependency_subclass import DependencySubclass
from pyrig.core.exceptions.dependency_subclass.multiple_found import (
    MultipleSubclassesFoundError,
)
from pyrig.rig import configs
from pyrig.rig.configs.base.config_file import ConfigFile
from pyrig.rig.configs.license import LicenseConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.configs.version_control.ignore import (
    VersionControllerIgnoreConfigFile,
)
from pyrig.rig.tests.mirror_test import MirrorTestConfigFile
from pyrig.rig.tools.base.tool import Tool


class TestDependencySubclass:
    """Test class."""

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
            VersionControllerIgnoreConfigFile,
        )
        result = ConfigFile.subclasses_sorted(*subclasses)
        assert result == [
            LicenseConfigFile,
            PyprojectConfigFile,
            VersionControllerIgnoreConfigFile,
        ]

    def test_I(self) -> None:  # noqa: N802
        """Test method."""
        result = VersionControllerIgnoreConfigFile.I
        assert isinstance(result, VersionControllerIgnoreConfigFile)
        assert result is VersionControllerIgnoreConfigFile.I.I

    def test_definition_package(self) -> None:
        """Test method."""
        result = ConfigFile.definition_package()
        assert issubclass(ConfigFile, DependencySubclass)
        assert result == configs

    def test_sorting_key(self) -> None:
        """Test method."""
        result = ConfigFile.sorting_key(PyprojectConfigFile)
        assert isinstance(result, (float, int))

        assert DependencySubclass.sorting_key(ConfigFile) == ConfigFile.__name__

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
        assert MirrorTestConfigFile.L.L is MirrorTestConfigFile

        with pytest.raises(MultipleSubclassesFoundError):
            _ = Tool.L
