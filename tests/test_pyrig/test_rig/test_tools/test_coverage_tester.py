"""module."""

from pyrig.rig.tools import coverage_tester
from pyrig.rig.tools.coverage_tester import CoverageTester


class TestCoverageTester:
    """Test class."""

    def test_additional_args(self) -> None:
        """Test method."""
        assert CoverageTester.I.additional_args() == (
            "--cov=pyrig",
            "--cov-report=term-missing",
            "--cov-fail-under=100",
        )

    def test_coverage_threshold(self) -> None:
        """Test method."""
        coverage_threshold = 90
        assert CoverageTester().coverage_threshold() == coverage_threshold
        override_threshold = 100
        assert CoverageTester.I.coverage_threshold() == override_threshold

    def test_coverage_color(self) -> None:
        """Test method."""
        assert CoverageTester().coverage_color() == (108, 80, 45)
        assert CoverageTester.I.coverage_color() == (120, 80, 45)

    def test_name(self) -> None:
        """Test method."""
        result = CoverageTester.I.name()
        assert result == "pytest-cov"

    def test_group(self) -> None:
        """Test method."""
        result = CoverageTester.I.group()
        assert isinstance(result, str)
        assert result == "testing"

    def test_badge_urls(self) -> None:
        """Test method."""
        result = CoverageTester.I.badge_urls()
        assert result == (
            "https://img.shields.io/badge/coverage->=100%25-hsl(120,80%25,45%25)?logo=codecov",
            "https://github.com/pytest-dev/pytest-cov",
        )


def test_module_docstring() -> None:
    """Test module docstring."""
    assert (
        coverage_tester.__doc__
        == """Coverage testing wrapper for the code coverage tool.

Wraps CoverageTester commands and information.
"""
    )
