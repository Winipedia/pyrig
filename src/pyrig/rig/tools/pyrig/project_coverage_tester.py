"""Override ProjectCoverageTester for pyrig project."""

from pyrig.core.introspection.packages import src_package_is_pyrig
from pyrig.rig.tools.project_coverage_tester import (
    ProjectCoverageTester as BaseProjectCoverageTester,
)

if src_package_is_pyrig():

    class ProjectCoverageTester(BaseProjectCoverageTester):
        """Pyrig-specific coverage tester.

        Extends base ProjectCoverageTester with pyrig-specific configuration

        Only used when pyrig is the current project (via conditional
        class definition). Other projects using pyrig as a dependency will use
        the base ProjectCoverageTester instead.
        """

        def coverage_threshold(self) -> int:
            """Get minimum test coverage percentage threshold."""
            return 100
