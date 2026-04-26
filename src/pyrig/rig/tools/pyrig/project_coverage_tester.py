"""Pyrig-specific coverage tester override.

The conditional class definition uses ``src_package_is_pyrig()`` to ensure
this override is only active when running within pyrig's repository. Other
projects using pyrig as a dependency keep the base threshold.
"""

from pyrig.core.introspection.packages import src_package_is_pyrig
from pyrig.rig.tools.project_coverage_tester import (
    ProjectCoverageTester as BaseProjectCoverageTester,
)

if src_package_is_pyrig():

    class ProjectCoverageTester(BaseProjectCoverageTester):
        """Pyrig-specific coverage tester.

        Overrides the base coverage threshold to require 100% test coverage.
        Only instantiated when pyrig is the current project (via conditional
        class definition). Other projects using pyrig as a dependency will use
        the base ``ProjectCoverageTester`` with the default threshold instead.
        """

        def coverage_threshold(self) -> int:
            """Get the minimum test coverage percentage threshold.

            Returns:
                100, requiring full test coverage for pyrig's own codebase.
            """
            return 100
