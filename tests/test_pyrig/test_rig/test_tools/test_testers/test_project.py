"""module."""

from pathlib import Path

from pyrig.rig.tools.testers.coverage import CoverageTester
from pyrig.rig.tools.testers.project import ProjectTester


class TestProjectTester:
    """Test class."""

    def test_additional_args(self) -> None:
        """Test method."""
        assert (
            ProjectTester.I.additional_args() == CoverageTester.I.additional_test_args()
        )

    def test_dev_dependencies(self) -> None:
        """Test method."""
        assert ProjectTester.I.dev_dependencies() == ("pytest",)

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            ProjectTester.I.image_url()
            == "https://img.shields.io/badge/tested%20with-pytest-46a2f1.svg?logo=pytest"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert ProjectTester.I.link_url() == "https://pytest.org"

    def test_version_control_ignore_paths(self) -> None:
        """Test method."""
        assert ProjectTester.I.version_control_ignore_paths() == (".pytest_cache/",)

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
        assert result == "testing"

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
