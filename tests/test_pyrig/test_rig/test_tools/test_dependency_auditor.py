"""module."""

from pyrig.rig.tools.dependency_auditor import DependencyAuditor


class TestDependencyAuditor:
    """Test class."""

    def test_group(self) -> None:
        """Test method."""
        result = DependencyAuditor.L.group()
        assert isinstance(result, str)
        assert result == "security"

    def test_badge_urls(self) -> None:
        """Test method."""
        result = DependencyAuditor.L.badge_urls()
        assert isinstance(result, tuple)
        assert all(isinstance(url, str) for url in result)

    def test_name(self) -> None:
        """Test method."""
        assert DependencyAuditor.L.name() == "pip-audit"

    def test_audit_args(self) -> None:
        """Test method."""
        args = DependencyAuditor.L.audit_args("--format", "json")
        assert args == ("pip-audit", "--format", "json")
