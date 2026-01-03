"""module."""

from pathlib import Path

from pyrig.dev.configs.dot_python_version import DotPythonVersionConfigFile


class TestDotPythonVersionConfigFile:
    """Test class."""

    def test_get_filename(self) -> None:
        """Test method for get_filename."""
        assert DotPythonVersionConfigFile.get_filename() == ""

    def test_get_file_extension(self) -> None:
        """Test method for get_file_extension."""
        assert DotPythonVersionConfigFile.get_file_extension() == "python-version"

    def test_get_parent_path(self) -> None:
        """Test method for get_parent_path."""
        assert DotPythonVersionConfigFile.get_parent_path() == Path()

    def test_get_lines(self) -> None:
        """Test method for get_lines."""
        lines = DotPythonVersionConfigFile.get_lines()
        assert len(lines) == 1

    def test_override_content(self) -> None:
        """Test method for override_content."""
        assert DotPythonVersionConfigFile.override_content()
