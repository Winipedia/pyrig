"""module."""

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.dependencies.auditor import DependencyAuditor


class TestDependencyAuditor:
    """Test class."""

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            DependencyAuditor.I.image_url()
            == "https://img.shields.io/badge/security-pip--audit-blue?logo=python"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert DependencyAuditor.I.link_url() == "https://github.com/pypa/pip-audit"

    def test_group(self) -> None:
        """Test method."""
        result = DependencyAuditor.I.group()
        assert isinstance(result, str)
        assert result == "code-quality"

    def test_name(self) -> None:
        """Test method."""
        assert DependencyAuditor.I.name() == "pip-audit"

    def test_audit_args(self) -> None:
        """Test method."""
        args = DependencyAuditor.I.audit_args("--format", "json")
        assert isinstance(args, Args)
