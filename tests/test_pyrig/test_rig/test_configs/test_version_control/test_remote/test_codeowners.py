"""Test module."""

from pathlib import Path

from pyrig.rig.configs.version_control.remote.codeowners import CodeownersConfigFile


class TestCodeownersConfigFile:
    """Test class."""

    def test_content(self) -> None:
        """Test method."""
        assert CodeownersConfigFile().content() == "* @Winipedia\n"

    def test_extension(self) -> None:
        """Test method."""
        assert CodeownersConfigFile().extension() == ""

    def test_extension_separator(self) -> None:
        """Test method."""
        assert CodeownersConfigFile.I.extension_separator() == ""

    def test_parent_path(self) -> None:
        """Test method."""
        assert CodeownersConfigFile().parent_path() == Path(".github")

    def test_stem(self) -> None:
        """Test method."""
        assert CodeownersConfigFile.I.stem() == "CODEOWNERS"
