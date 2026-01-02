"""module."""

from pyrig.dev.management.security_checker import SecurityChecker


class TestSecurityChecker:
    """Test class."""

    def test_name(self) -> None:
        """Test method."""
        result = SecurityChecker.name()
        assert result == "bandit"

    def test_get_run_args(self) -> None:
        """Test method."""
        result = SecurityChecker.get_run_args()
        assert result == ("bandit",)

    def test_get_run_with_config_args(self) -> None:
        """Test method."""
        result = SecurityChecker.get_run_with_config_args()
        assert result == ("bandit", "-c", "pyproject.toml", "-r", ".")
