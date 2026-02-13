"""module."""

from pyrig.rig.tools.project_coverage_tester import ProjectCoverageTester


class TestProjectCoverageTester:
    """Test class."""

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
