"""module."""

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.dependencies.auditor import DependencyAuditor
from pyrig.rig.tools.typing.checker import TypeChecker
from pyrig.rig.tools.version_control.hooks.manager import VersionControlHookManager


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

    def test_check_args(self) -> None:
        """Test method."""
        args = DependencyAuditor.I.check_args("--format", "json")
        assert isinstance(args, Args)

    def test_check_hook(self) -> None:
        """Test method."""
        # runs on transition stages, but ties its priority to the checks tier
        hook = DependencyAuditor.I.check_hook()
        types_hook = TypeChecker.I.check_hook()
        assert hook["priority"] == types_hook["priority"]
        assert hook["stages"] == VersionControlHookManager.I.transition_stages()
        assert hook["always_run"] is True
        assert hook["pass_filenames"] is False

    def test_audit_dependencies(self) -> None:
        """Test method."""
        assert (
            DependencyAuditor.I.audit_dependencies() == DependencyAuditor.I.check_args()
        )
