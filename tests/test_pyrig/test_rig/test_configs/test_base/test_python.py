"""module."""

from pyrig.rig.configs.base.python import PythonConfigFile


class TestPythonConfigFile:
    """Test class."""

    def test_extension(self) -> None:
        """Test method."""
        expected = "py"
        actual = PythonConfigFile.extension()
        assert actual == expected, f"Expected {expected}, got {actual}"
