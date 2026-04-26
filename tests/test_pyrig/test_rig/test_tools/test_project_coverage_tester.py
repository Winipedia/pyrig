"""module."""

from pyrig.rig.tools import project_coverage_tester
from pyrig.rig.tools.project_coverage_tester import ProjectCoverageTester


class TestProjectCoverageTester:
    """Test class."""

    def test_access_token_key(self) -> None:
        """Test method."""
        assert ProjectCoverageTester.I.access_token_key() == "CODECOV_TOKEN"

    def test_additional_args(self) -> None:
        """Test method."""
        assert ProjectCoverageTester.I.additional_args() == (
            "--cov=pyrig",
            "--cov-report=term-missing",
            "--cov-fail-under=100",
        )

    def test_additional_ci_args(self) -> None:
        """Test method."""
        assert ProjectCoverageTester.I.additional_ci_args() == ("--cov-report=xml",)

    def test_coverage_threshold(self) -> None:
        """Test method."""
        coverage_threshold = 90
        assert ProjectCoverageTester().coverage_threshold() == coverage_threshold
        override_threshold = 100
        assert ProjectCoverageTester.I.coverage_threshold() == override_threshold

    def test_name(self) -> None:
        """Test method."""
        result = ProjectCoverageTester.I.name()
        assert result == "pytest-cov"

    def test_group(self) -> None:
        """Test method."""
        result = ProjectCoverageTester.I.group()
        assert isinstance(result, str)
        assert result == "testing"

    def test_badge_urls(self) -> None:
        """Test method."""
        result = ProjectCoverageTester.I.badge_urls()
        assert isinstance(result, tuple)
        assert all(isinstance(url, str) for url in result)

    def test_remote_coverage_url(self) -> None:
        """Test method."""
        result = ProjectCoverageTester.I.remote_coverage_url()
        assert isinstance(result, str)
        assert result.startswith("https://codecov.io/gh/")


def test_module_docstring() -> None:
    """Test module docstring."""
    assert (
        project_coverage_tester.__doc__
        == """Coverage testing wrapper for pytest-cov and Codecov.io integration.

Wraps ProjectCoverageTester commands and information.
"""
    )
