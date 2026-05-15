"""Test module."""

from pyrig.rig.tools.coverage_tester import (
    CoverageTester as BaseCoverageTester,
)
from pyrig.rig.tools.pyrig.coverage_tester import CoverageTester


class TestCoverageTester:
    """Test class."""

    def test_threshold(self) -> None:
        """Test method."""
        threshold = 100
        assert BaseCoverageTester.I.threshold() == threshold
        assert BaseCoverageTester.L is CoverageTester
