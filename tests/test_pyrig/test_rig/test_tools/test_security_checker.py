"""module."""

from pyrig.rig.tools.security_checker import SecurityChecker


class TestSecurityChecker:
    """Test class."""

    def test_get_group(self) -> None:
        """Test method."""
        result = SecurityChecker.L.get_group()
        assert isinstance(result, str)
        assert result == "security"

    def test_get_badge_urls(self) -> None:
        """Test method."""
        result = SecurityChecker.L.get_badge_urls()
        assert isinstance(result, tuple)
        assert all(isinstance(url, str) for url in result)

    def test_get_name(self) -> None:
        """Test method."""
        result = SecurityChecker.L.get_name()
        assert result == "bandit"

    def test_get_run_args(self) -> None:
        """Test method."""
        result = SecurityChecker.L.get_run_args()
        assert result == ("bandit",)

    def test_get_run_with_config_args(self) -> None:
        """Test method."""
        result = SecurityChecker.L.get_run_with_config_args()
        assert result == ("bandit", "-c", "pyproject.toml", "-r", ".")
