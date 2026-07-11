"""module."""

from pyrig.rig.tools.linting.security import SecurityLinter


class TestSecurityLinter:
    """Test class."""

    def test_group(self) -> None:
        """Test method."""
        result = SecurityLinter.I.group()
        assert isinstance(result, str)
        assert result == "code-quality"

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            SecurityLinter.I.image_url()
            == "https://img.shields.io/badge/security-bandit-yellow.svg"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert SecurityLinter.I.link_url() == "https://github.com/PyCQA/bandit"

    def test_name(self) -> None:
        """Test method."""
        result = SecurityLinter.I.name()
        assert result == "bandit"

    def test_check_args(self) -> None:
        """Test method."""
        result = SecurityLinter.I.check_args("flag1", "flag2")
        assert result == ("bandit", "flag1", "flag2", "-r", "src/pyrig")
