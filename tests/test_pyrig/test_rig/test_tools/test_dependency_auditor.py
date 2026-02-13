"""module."""

from pyrig.rig.tools.dependency_auditor import DependencyAuditor


class TestDependencyAuditor:
    """Test class."""

    def test_group(self) -> None:
        """Test method."""
        result = DependencyAuditor.I.group()
        assert isinstance(result, str)
        assert result == "security"

    def test_badge_urls(self) -> None:
        """Test method."""
        result = DependencyAuditor.I.badge_urls()
        assert isinstance(result, tuple)
        assert all(isinstance(url, str) for url in result)

    def test_name(self) -> None:
        """Test method."""
        assert DependencyAuditor.I.name() == "pip-audit"

    def test_audit_args(self) -> None:
        """Test method."""
        args = DependencyAuditor.I.audit_args("--format", "json")
        assert args == ("pip-audit", "--format", "json")
