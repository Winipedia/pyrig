"""module."""

from pyrig.rig.tools.dependency_auditor import DependencyAuditor


class TestDependencyAuditor:
    """Test class."""

    def test_name(self) -> None:
        """Test method."""
        assert DependencyAuditor.L.name() == "pip-audit"

    def test_get_audit_args(self) -> None:
        """Test method."""
        args = DependencyAuditor.L.get_audit_args("--format", "json")
        assert args == ("pip-audit", "--format", "json")
