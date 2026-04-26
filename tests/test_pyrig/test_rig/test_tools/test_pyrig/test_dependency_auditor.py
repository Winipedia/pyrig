"""Test module."""

from pyrig.rig.tools.dependency_auditor import (
    DependencyAuditor as BaseDependencyAuditor,
)
from pyrig.rig.tools.pyrig.dependency_auditor import DependencyAuditor


class TestDependencyAuditor:
    """Test class."""

    def test_audit_args(self) -> None:
        """Test method."""
        args = DependencyAuditor.I.audit_args()
        ignore_vulns_indexes = [
            i + 1 for i, arg in enumerate(args) if arg == "--ignore-vuln"
        ]
        vulns = [args[i] for i in ignore_vulns_indexes]
        # run pip-audit without the flags and assert that all vulns are in the result
        # so if this test fails then we need to adjust the override vulns
        base_args = BaseDependencyAuditor().audit_args()
        result = base_args.run(check=False)
        content = result.stdout + result.stderr
        for vuln in vulns:
            assert (
                vuln in content
            ), f"""Expected vulnerability {vuln} to be in pip-audit output.
This probably means the vulnerability is no longer relevant
and the override should be updated to no longer ignore it."""
