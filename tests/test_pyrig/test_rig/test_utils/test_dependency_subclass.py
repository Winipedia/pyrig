"""Test module."""

import pyrig
from pyrig import rig
from pyrig.rig.utils.dependency_subclass import RigDependencySubclass


class TestRigDependencySubclass:
    """Test class."""

    def test_definition_package(self) -> None:
        """Test method."""
        assert RigDependencySubclass.definition_package() is rig

    def test_base_dependency(self) -> None:
        """Test method."""
        assert RigDependencySubclass.base_dependency() is pyrig
