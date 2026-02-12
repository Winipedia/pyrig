"""module."""

from pathlib import Path

from pyrig.rig.configs.dot_python_version import DotPythonVersionConfigFile


class TestDotPythonVersionConfigFile:
    """Test class."""

    def test_get_filename(self) -> None:
        """Test method."""
        assert DotPythonVersionConfigFile.get_filename() == ""

    def test_get_file_extension(self) -> None:
        """Test method."""
        assert DotPythonVersionConfigFile.get_file_extension() == "python-version"

    def test_get_parent_path(self) -> None:
        """Test method."""
        assert DotPythonVersionConfigFile.get_parent_path() == Path()

    def test_get_lines(self) -> None:
        """Test method."""
        lines = DotPythonVersionConfigFile.get_lines()
        assert len(lines) == 1

    def test_override_content(self) -> None:
        """Test method."""
        assert DotPythonVersionConfigFile.override_content()
