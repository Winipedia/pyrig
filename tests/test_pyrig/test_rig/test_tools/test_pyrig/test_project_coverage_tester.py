"""Test module."""

from pyrig.rig.tools.project_coverage_tester import (
    ProjectCoverageTester as BaseProjectCoverageTester,
)
from pyrig.rig.tools.pyrig.project_coverage_tester import ProjectCoverageTester


class TestProjectCoverageTester:
    """Test class."""

    def test_coverage_threshold(self) -> None:
        """Test method."""
        coverage_threshold = 100
        assert BaseProjectCoverageTester.I.coverage_threshold() == coverage_threshold
        assert BaseProjectCoverageTester.L is ProjectCoverageTester
