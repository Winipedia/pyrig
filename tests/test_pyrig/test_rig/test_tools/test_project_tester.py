"""module."""

from pyrig.rig.tools.project_tester import ProjectTester


class TestProjectTester:
    """Test class."""

    def test_get_dev_dependencies(self) -> None:
        """Test method."""
        result = ProjectTester.L.get_dev_dependencies()
        assert result == ["pytest", "pytest-cov", "pytest-mock"]

    def test_get_test_args(self) -> None:
        """Test method."""
        result = ProjectTester.L.get_test_args()
        assert result == ("pytest",)

    def test_get_coverage_threshold(self) -> None:
        """Test method."""
        result = ProjectTester.L.get_coverage_threshold()
        expected = 90
        assert result == expected

    def test_name(self) -> None:
        """Test method."""
        result = ProjectTester.L.name()
        assert result == "pytest"

    def test_get_run_tests_in_ci_args(self) -> None:
        """Test method."""
        result = ProjectTester.L.get_run_tests_in_ci_args()
        assert result == (
            "pytest",
            "--log-cli-level=INFO",
            "--cov-report=xml",
        )
