"""module."""

from pathlib import Path

from pyrig.rig.tools.project_tester import ProjectTester


class TestProjectTester:
    """Test class."""

    def test_additional_args(self) -> None:
        """Test method."""
        assert tuple(ProjectTester().additional_args()) == (
            "--cov=pyrig",
            "--cov-branch",
            "--cov-fail-under=90",
            "--cov-report=term-missing:skip-covered",
        )
        assert str(ProjectTester().additional_args()) == (
            "--cov=pyrig --cov-branch --cov-fail-under=90"
            " --cov-report=term-missing:skip-covered"
        )

    def test_threshold(self) -> None:
        """Test method."""
        threshold = 90
        assert ProjectTester().threshold() == threshold
        override_threshold = 100
        assert ProjectTester.I.threshold() == override_threshold

    def test_color(self) -> None:
        """Test method."""
        assert ProjectTester().color() == (108, 80, 45)
        assert ProjectTester.I.color() == (120, 80, 45)

    def test_dev_dependencies(self) -> None:
        """Test method."""
        assert ProjectTester.I.dev_dependencies() == ("pytest", "pytest-cov")

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            ProjectTester().image_url()
            == "https://img.shields.io/badge/coverage->=90%25-hsl(108,80%25,45%25)?logo=codecov&logoColor=white"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert ProjectTester().link_url() == "https://pytest.org"

    def test_version_control_ignore_paths(self) -> None:
        """Test method."""
        assert ProjectTester().version_control_ignore_paths() == (
            ".pytest_cache/",
            ".coverage",
        )

    def test_source_root(self) -> None:
        """Test method."""
        assert ProjectTester.I.source_root() == Path()

    def test_package_root(self) -> None:
        """Test method."""
        assert ProjectTester.I.package_root() == Path("tests")

    def test_group(self) -> None:
        """Test method."""
        result = ProjectTester.I.group()
        assert isinstance(result, str)
        assert result == "project-status"

    def test_test_args(self) -> None:
        """Test method."""
        result = ProjectTester.I.test_args()
        assert result == ("pytest",)

    def test_name(self) -> None:
        """Test method."""
        result = ProjectTester.I.name()
        assert result == "pytest"

    def test_package_name(self) -> None:
        """Test method."""
        result = ProjectTester.I.package_name()
        assert result == "tests"
