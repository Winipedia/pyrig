"""module."""

from pathlib import Path

from pyrig.rig.tools.project_tester import ProjectTester


class TestProjectTester:
    """Test class."""

    def test_test_module_prefix(self) -> None:
        """Test method."""
        assert ProjectTester.I.test_module_prefix() == "test_"

    def test_tests_source_root(self) -> None:
        """Test method."""
        assert ProjectTester.I.tests_source_root() == Path()

    def test_tests_package_root(self) -> None:
        """Test method."""
        assert ProjectTester.I.tests_package_root() == Path("tests")

    def test_group(self) -> None:
        """Test method."""
        result = ProjectTester.I.group()
        assert isinstance(result, str)
        assert result == "testing"

    def test_badge_urls(self) -> None:
        """Test method."""
        result = ProjectTester.I.badge_urls()
        assert isinstance(result, tuple)
        assert all(isinstance(url, str) for url in result)

    def test_dev_dependencies(self) -> None:
        """Test method."""
        result = ProjectTester.I.dev_dependencies()
        assert result == ("pytest", "pytest-mock")

    def test_test_args(self) -> None:
        """Test method."""
        result = ProjectTester.I.test_args()
        assert result == ("pytest",)

    def test_name(self) -> None:
        """Test method."""
        result = ProjectTester.I.name()
        assert result == "pytest"

    def test_run_tests_in_ci_args(self) -> None:
        """Test method."""
        result = ProjectTester.I.run_tests_in_ci_args()
        assert result == (
            "pytest",
            "--log-cli-level=INFO",
            "--cov-report=xml",
        )

    def test_tests_package_name(self) -> None:
        """Test method."""
        result = ProjectTester.I.tests_package_name()
        assert result == "tests"
