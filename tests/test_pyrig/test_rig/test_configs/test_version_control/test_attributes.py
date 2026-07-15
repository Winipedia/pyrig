"""Test module."""

from pathlib import Path

from pyrig.rig.configs.version_control.attributes import (
    VersionControllerAttributesConfigFile,
)


class TestVersionControllerAttributesConfigFile:
    """Test class."""

    def test_content(self) -> None:
        """Test method."""
        content = VersionControllerAttributesConfigFile.I.content()
        assert content.startswith("* text=auto eol=lf")

    def test_extension(self) -> None:
        """Test method."""
        assert VersionControllerAttributesConfigFile.I.extension() == ""

    def test_extension_separator(self) -> None:
        """Test method."""
        assert VersionControllerAttributesConfigFile.I.extension_separator() == ""

    def test_parent_path(self) -> None:
        """Test method."""
        assert VersionControllerAttributesConfigFile.I.parent_path() == Path()

    def test_stem(self) -> None:
        """Test method."""
        assert VersionControllerAttributesConfigFile.I.stem() == ".gitattributes"
