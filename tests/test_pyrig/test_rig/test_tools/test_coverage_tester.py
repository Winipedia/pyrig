"""module."""

from pyrig.rig.tools import coverage_tester
from pyrig.rig.tools.coverage_tester import CoverageTester


class TestCoverageTester:
    """Test class."""

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            CoverageTester.I.image_url()
            == "https://img.shields.io/badge/coverage->=100%25-hsl(120,80%25,45%25)?logo=codecov&logoColor=white"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert CoverageTester.I.link_url() == "https://github.com/pytest-dev/pytest-cov"

    def test_version_control_ignore_paths(self) -> None:
        """Test method."""
        assert CoverageTester.I.version_control_ignore_paths() == (".coverage",)

    def test_additional_test_args(self) -> None:
        """Test method."""
        assert tuple(CoverageTester.I.additional_test_args()) == (
            "--cov=pyrig",
            "--cov-branch",
            "--cov-report=term-missing",
            "--cov-fail-under=100",
        )
        assert (
            str(CoverageTester.I.additional_test_args())
            == "--cov=pyrig --cov-branch --cov-report=term-missing --cov-fail-under=100"
        )

    def test_threshold(self) -> None:
        """Test method."""
        threshold = 90
        assert CoverageTester().threshold() == threshold
        override_threshold = 100
        assert CoverageTester.I.threshold() == override_threshold

    def test_color(self) -> None:
        """Test method."""
        assert CoverageTester().color() == (108, 80, 45)
        assert CoverageTester.I.color() == (120, 80, 45)

    def test_name(self) -> None:
        """Test method."""
        result = CoverageTester.I.name()
        assert result == "pytest-cov"

    def test_group(self) -> None:
        """Test method."""
        result = CoverageTester.I.group()
        assert isinstance(result, str)
        assert result == "testing"


def test_module_docstring() -> None:
    """Test module docstring."""
    assert (
        coverage_tester.__doc__
        == """Coverage testing wrapper for the code coverage tool.

Wraps CoverageTester commands and information.
"""
    )
