"""Test module."""

from pyrig.core.exceptions.base.dependency_subclass import DependencySubclassError


class TestDependencySubclassError:
    """Test class."""

    def test_command_recommendation(self) -> None:
        """Test method."""
        assert "pyrig subcls" in DependencySubclassError().command_recommendation()
