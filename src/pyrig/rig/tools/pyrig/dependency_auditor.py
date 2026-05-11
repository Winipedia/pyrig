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

            It is used to ignore irrelevant vulnerabilities in dependencies,
            so that the CI/CD passes the dependency audit check. It delegates
            to the base whenever nothing needs to be ignored.
            """
            return super().audit_args(*args)
