"""module."""

from pathlib import Path

from pyrig.dev.configs.markdown.security import SecurityConfigFile


class TestSecurityConfigFile:
    """Test class."""

    def test_get_filename(self) -> None:
        """Test method."""
        result = SecurityConfigFile.get_filename()
        assert result == "SECURITY"

    def test_get_parent_path(self) -> None:
        """Test method."""
        result = SecurityConfigFile.get_parent_path()
        assert result == Path()

    def test_get_lines(self) -> None:
        """Test method."""
        result = SecurityConfigFile.get_lines()
        assert len(result) > 0

    def test_is_correct(self) -> None:
        """Test method."""
        result = SecurityConfigFile.is_correct()
        assert result

    def test_get_security_template_with_contact_method(self) -> None:
        """Test method."""
        result = SecurityConfigFile.get_security_template_with_contact_method()
        assert len(result) > 0

    def test_get_contact_method(self) -> None:
        """Test method."""
        result = SecurityConfigFile.get_contact_method()
        assert len(result) > 0
