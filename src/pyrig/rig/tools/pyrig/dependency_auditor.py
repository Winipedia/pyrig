"""Pyrig specific dependency auditor override."""

from pyrig.core.introspection.packages import src_package_is_pyrig
from pyrig.core.subprocesses import Args
from pyrig.rig.tools.dependency_auditor import (
    DependencyAuditor as BaseDependencyAuditor,
)

if src_package_is_pyrig():

    class DependencyAuditor(BaseDependencyAuditor):
        """Pyrig-specific dependency auditor.

        Overrides the base DependencyAuditor to apply pyrig-specific overrides.
        """

        def audit_args(self, *args: str) -> Args:
            """Override pip-audit command arguments construction.

            Currently delegates to the base implementation. Can be overridden
            to ignore specific vulnerabilities when needed for CI/CD.
            """
            return super().audit_args(*args)
