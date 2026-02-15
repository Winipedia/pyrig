"""module."""

from pathlib import Path

from pyrig.rig.configs.dot_python_version import DotPythonVersionConfigFile


class TestDotPythonVersionConfigFile:
    """Test class."""

    def test_filename(self) -> None:
        """Test method."""
        assert DotPythonVersionConfigFile.I.filename() == ""

    def test_extension(self) -> None:
        """Test method."""
        assert DotPythonVersionConfigFile.I.extension() == "python-version"

    def test_parent_path(self) -> None:
        """Test method."""
        assert DotPythonVersionConfigFile.I.parent_path() == Path()

    def test_lines(self) -> None:
        """Test method."""
        lines = DotPythonVersionConfigFile.I.lines()
        assert len(lines) == 1

    def test_should_override_content(self) -> None:
        """Test method."""
        assert DotPythonVersionConfigFile.I.should_override_content()
