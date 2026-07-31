"""module."""

from pathlib import Path

from pyrig.rig.configs.community.security import SecurityConfigFile


class TestSecurityConfigFile:
    """Test class."""

    def test_stem(self) -> None:
        """Test method."""
        result = SecurityConfigFile.I.stem()
        assert result == "SECURITY"

    def test_parent_path(self) -> None:
        """Test method."""
        result = SecurityConfigFile.I.parent_path()
        assert result == Path()

    def test_content(self) -> None:
        """Test method."""
        result = SecurityConfigFile.I.content()
        assert len(result) > 0
        assert "<winipedia@gmx.de>." in result

    def test_contact_method(self) -> None:
        """Test method."""
        assert SecurityConfigFile.I.contact_method() == "<winipedia@gmx.de>"
