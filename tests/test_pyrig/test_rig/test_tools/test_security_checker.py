"""module."""

from pyrig.rig.tools.security_checker import SecurityChecker


class TestSecurityChecker:
    """Test class."""

    def test_group(self) -> None:
        """Test method."""
        result = SecurityChecker.I.group()
        assert isinstance(result, str)
        assert result == "security"

    def test_badge_urls(self) -> None:
        """Test method."""
        result = SecurityChecker.I.badge_urls()
        assert isinstance(result, tuple)
        assert all(isinstance(url, str) for url in result)

    def test_name(self) -> None:
        """Test method."""
        result = SecurityChecker.I.name()
        assert result == "bandit"

    def test_run_args(self) -> None:
        """Test method."""
        result = SecurityChecker.I.run_args()
        assert result == ("bandit",)

    def test_run_with_config_args(self) -> None:
        """Test method."""
        result = SecurityChecker.I.run_with_config_args()
        assert result == ("bandit", "-c", "pyproject.toml", "-r", ".")
