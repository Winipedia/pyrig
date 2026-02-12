"""module."""

from pyrig.rig.configs.base.python import PythonConfigFile


class TestPythonConfigFile:
    """Test class."""

    def test_get_file_extension(self) -> None:
        """Test method."""
        expected = "py"
        actual = PythonConfigFile.get_file_extension()
        assert actual == expected, f"Expected {expected}, got {actual}"
