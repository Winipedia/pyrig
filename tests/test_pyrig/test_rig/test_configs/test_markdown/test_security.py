"""module."""

from pathlib import Path

from pyrig.rig.configs.markdown.security import SecurityConfigFile


class TestSecurityConfigFile:
    """Test class."""

    def test_filename(self) -> None:
        """Test method."""
        result = SecurityConfigFile.filename()
        assert result == "SECURITY"

    def test_parent_path(self) -> None:
        """Test method."""
        result = SecurityConfigFile.parent_path()
        assert result == Path()

    def test_lines(self) -> None:
        """Test method."""
        result = SecurityConfigFile.lines()
        assert len(result) > 0

    def test_is_correct(self) -> None:
        """Test method."""
        result = SecurityConfigFile.is_correct()
        assert result

    def test_template_with_contact_method(self) -> None:
        """Test method."""
        result = SecurityConfigFile.template_with_contact_method()
        assert len(result) > 0

    def test_contact_method(self) -> None:
        """Test method."""
        result = SecurityConfigFile.contact_method()
        assert len(result) > 0
