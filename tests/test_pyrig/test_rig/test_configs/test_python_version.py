"""module."""

from pathlib import Path

from pyrig.rig.configs.python_version import PythonVersionConfigFile


class TestPythonVersionConfigFile:
    """Test class."""

    def test_extension_separator(self) -> None:
        """Test method."""
        assert PythonVersionConfigFile.I.extension_separator() == ""

    def test_stem(self) -> None:
        """Test method."""
        assert PythonVersionConfigFile.I.stem() == ".python-version"

    def test_extension(self) -> None:
        """Test method."""
        assert PythonVersionConfigFile.I.extension() == ""

    def test_parent_path(self) -> None:
        """Test method."""
        assert PythonVersionConfigFile.I.parent_path() == Path()

    def test_lines(self) -> None:
        """Test method."""
        lines = PythonVersionConfigFile.I.lines()
        assert lines == ["3.12", ""]

    def test_should_override_content(self) -> None:
        """Test method."""
        assert PythonVersionConfigFile.I.should_override_content()
