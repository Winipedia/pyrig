"""module."""

from pyrig.rig.tools.dependency_auditor import DependencyAuditor


class TestDependencyAuditor:
    """Test class."""

    def test_get_group(self) -> None:
        """Test method."""
        result = DependencyAuditor.L.get_group()
        assert isinstance(result, str)
        assert result == "security"

    def test_get_badge_urls(self) -> None:
        """Test method."""
        result = DependencyAuditor.L.get_badge_urls()
        assert isinstance(result, tuple)
        assert all(isinstance(url, str) for url in result)

    def test_name(self) -> None:
        """Test method."""
        assert DependencyAuditor.L.name() == "pip-audit"

    def test_get_audit_args(self) -> None:
        """Test method."""
        args = DependencyAuditor.L.get_audit_args("--format", "json")
        assert args == ("pip-audit", "--format", "json")
