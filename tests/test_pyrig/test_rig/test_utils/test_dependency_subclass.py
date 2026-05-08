"""Test module."""

from pyrig import rig
from pyrig.rig.utils.dependency_subclass import RigDependencySubclass


class TestRigDependencySubclass:
    """Test class."""

    def test_dependency_package(self) -> None:
        """Test method."""
        assert RigDependencySubclass.dependency_package() is rig
