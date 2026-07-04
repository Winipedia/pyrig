"""module."""

from pyrig.rig.tools.security_checker import SecurityChecker


class TestSecurityChecker:
    """Test class."""

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            SecurityChecker.I.image_url()
            == "https://img.shields.io/badge/security-bandit-yellow.svg"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert SecurityChecker.I.link_url() == "https://github.com/PyCQA/bandit"

    def test_group(self) -> None:
        """Test method."""
        result = SecurityChecker.I.group()
        assert isinstance(result, str)
        assert result == "code-quality"

    def test_name(self) -> None:
        """Test method."""
        result = SecurityChecker.I.name()
        assert result == "bandit"

    def test_check_args(self) -> None:
        """Test method."""
        result = SecurityChecker.I.check_args("flag1", "flag2")
        assert result == ("bandit", "flag1", "flag2", "-r", "src/pyrig")
