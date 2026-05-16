"""Test module."""

from pytest_mock import MockerFixture

from pyrig.core.introspection.modules import reimport_module
from pyrig.core.introspection.packages import src_package_is_package
from pyrig.rig.tools.coverage_tester import (
    CoverageTester as BaseCoverageTester,
)
from pyrig.rig.tools.pyrig import coverage_tester
from pyrig.rig.tools.pyrig.coverage_tester import CoverageTester


class TestCoverageTester:
    """Test class."""

    def test_threshold(self, mocker: MockerFixture) -> None:
        """Test method."""
        threshold = 100
        assert BaseCoverageTester.I.threshold() == threshold
        assert BaseCoverageTester.L is CoverageTester

        mock_src_package_is_package = mocker.patch(
            src_package_is_package.__module__ + "." + src_package_is_package.__name__,
            return_value=False,
        )
        assert hasattr(coverage_tester, CoverageTester.__name__)
        module = reimport_module(coverage_tester)
        mock_src_package_is_package.assert_called_once()
        assert not hasattr(module, CoverageTester.__name__)
