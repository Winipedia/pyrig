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

    def test_content(self) -> None:
        """Test method."""
        content = PythonVersionConfigFile.I.content()
        assert content == "3.12\n"
