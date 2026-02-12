"""module."""

from pyrig.rig.tools.project_tester import ProjectTester


class TestProjectTester:
    """Test class."""

    def test_group(self) -> None:
        """Test method."""
        result = ProjectTester.L.group()
        assert isinstance(result, str)
        assert result == "testing"

    def test_badge_urls(self) -> None:
        """Test method."""
        result = ProjectTester.L.badge_urls()
        assert isinstance(result, tuple)
        assert all(isinstance(url, str) for url in result)

    def test_dev_dependencies(self) -> None:
        """Test method."""
        result = ProjectTester.L.dev_dependencies()
        assert result == ["pytest", "pytest-mock"]

    def test_get_test_args(self) -> None:
        """Test method."""
        result = ProjectTester.L.get_test_args()
        assert result == ("pytest",)

    def test_coverage_threshold(self) -> None:
        """Test method."""
        result = ProjectTester.L.coverage_threshold()
        expected = 90
        assert result == expected

    def test_name(self) -> None:
        """Test method."""
        result = ProjectTester.L.name()
        assert result == "pytest"

    def test_run_tests_in_ci_args(self) -> None:
        """Test method."""
        result = ProjectTester.L.run_tests_in_ci_args()
        assert result == (
            "pytest",
            "--log-cli-level=INFO",
            "--cov-report=xml",
        )
