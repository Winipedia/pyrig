"""module."""

from pyrig.dev.management.project_tester import ProjectTester


class TestProjectTester:
    """Test class."""

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
