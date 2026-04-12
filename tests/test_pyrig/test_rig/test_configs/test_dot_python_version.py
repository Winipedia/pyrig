"""module."""

from pathlib import Path

from pyrig.rig.configs.dot_python_version import DotPythonVersionConfigFile


class TestDotPythonVersionConfigFile:
    """Test class."""

    def test_extension_separator(self) -> None:
        """Test method."""
        assert DotPythonVersionConfigFile.I.extension_separator() == ""

    def test_stem(self) -> None:
        """Test method."""
        assert DotPythonVersionConfigFile.I.stem() == ".python-version"

    def test_extension(self) -> None:
        """Test method."""
        assert DotPythonVersionConfigFile.I.extension() == ""

    def test_parent_path(self) -> None:
        """Test method."""
        assert DotPythonVersionConfigFile.I.parent_path() == Path()

    def test_lines(self) -> None:
        """Test method."""
        lines = DotPythonVersionConfigFile.I.lines()
        assert lines == ["3.12", ""]

    def test_should_override_content(self) -> None:
        """Test method."""
        assert DotPythonVersionConfigFile.I.should_override_content()
