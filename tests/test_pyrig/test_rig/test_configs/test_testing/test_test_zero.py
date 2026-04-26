"""module."""

from pathlib import Path

from pyrig.rig.configs.testing.test_zero import ZeroTestConfigFile
from pyrig.rig.tests import test_zero


class TestZeroTestConfigFile:
    """Test class."""

    def test_is_correct(self) -> None:
        """Test method."""
        assert ZeroTestConfigFile().is_correct()

    def test_parent_path(self) -> None:
        """Test method."""
        assert ZeroTestConfigFile().parent_path() == Path("tests")

    def test_copy_module(self) -> None:
        """Test method."""
        assert ZeroTestConfigFile().copy_module() is test_zero
