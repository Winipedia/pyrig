"""module."""

from pyrig.rig.configs.base.python import PythonConfigFile
from pyrig.rig.configs.python.main import MainConfigFile


class TestPythonConfigFile:
    """Test class."""

    def test_extension(self) -> None:
        """Test method."""
        expected = "py"
        assert issubclass(MainConfigFile, PythonConfigFile), (
            "MainConfigFile should inherit from PythonConfigFile"
        )
        actual = MainConfigFile().extension()
        assert actual == expected, f"Expected {expected}, got {actual}"
