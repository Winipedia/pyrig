"""module."""

from pyrig.rig.configs.base.python import PythonConfigFile
from pyrig.rig.configs.testing.zero_test import ZeroTestConfigFile


class TestPythonConfigFile:
    """Test class."""

    def test_extension(self) -> None:
        """Test method."""
        expected = "py"
        assert issubclass(ZeroTestConfigFile, PythonConfigFile)
        actual = ZeroTestConfigFile().extension()
        assert actual == expected, f"Expected {expected}, got {actual}"
