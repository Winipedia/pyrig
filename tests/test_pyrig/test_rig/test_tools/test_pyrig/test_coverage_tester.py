"""Test module."""

from pyrig.rig.tools.coverage_tester import (
    CoverageTester as BaseCoverageTester,
)
from pyrig.rig.tools.pyrig.coverage_tester import CoverageTester


class TestCoverageTester:
    """Test class."""

    def test_coverage_threshold(self) -> None:
        """Test method."""
        coverage_threshold = 100
        assert BaseCoverageTester.I.coverage_threshold() == coverage_threshold
        assert BaseCoverageTester.L is CoverageTester
