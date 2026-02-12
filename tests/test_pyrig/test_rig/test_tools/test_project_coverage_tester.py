"""module."""

from pyrig.rig.tools.project_coverage_tester import ProjectCoverageTester


class TestProjectCoverageTester:
    """Test class."""

    def test_get_name(self) -> None:
        """Test method."""
        result = ProjectCoverageTester.L.get_name()
        assert result == "pytest-cov"

    def test_get_group(self) -> None:
        """Test method."""
        result = ProjectCoverageTester.L.get_group()
        assert isinstance(result, str)
        assert result == "testing"

    def test_get_badge_urls(self) -> None:
        """Test method."""
        result = ProjectCoverageTester.L.get_badge_urls()
        assert isinstance(result, tuple)
        assert all(isinstance(url, str) for url in result)

    def test_get_remote_coverage_url(self) -> None:
        """Test method."""
        result = ProjectCoverageTester.L.get_remote_coverage_url()
        assert isinstance(result, str)
        assert result.startswith("https://codecov.io/gh/")
