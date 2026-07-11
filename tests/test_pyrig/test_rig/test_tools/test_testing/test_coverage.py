"""module."""

from pyrig.rig.tools.testing.coverage import CoverageTester


class TestCoverageTester:
    """Test class."""

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            CoverageTester().image_url()
            == "https://img.shields.io/badge/coverage->=90%25-hsl(108,80%25,45%25)?logo=codecov&logoColor=white"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert CoverageTester().link_url() == "https://github.com/pytest-dev/pytest-cov"

    def test_version_control_ignore_paths(self) -> None:
        """Test method."""
        assert CoverageTester().version_control_ignore_paths() == (".coverage",)

    def test_additional_test_args(self) -> None:
        """Test method."""
        assert tuple(CoverageTester().additional_test_args()) == (
            "--cov=pyrig",
            "--cov-branch",
            "--cov-fail-under=90",
            "--cov-report=term-missing:skip-covered",
        )
        assert str(CoverageTester().additional_test_args()) == (
            "--cov=pyrig --cov-branch --cov-fail-under=90"
            " --cov-report=term-missing:skip-covered"
        )

    def test_threshold(self) -> None:
        """Test method."""
        threshold = 90
        assert CoverageTester().threshold() == threshold
        override_threshold = 100
        assert CoverageTester.I.threshold() == override_threshold

    def test_color(self) -> None:
        """Test method."""
        assert CoverageTester().color() == (108, 80, 45)
        assert CoverageTester.I.color() == (120, 80, 45)

    def test_name(self) -> None:
        """Test method."""
        result = CoverageTester.I.name()
        assert result == "pytest-cov"

    def test_group(self) -> None:
        """Test method."""
        result = CoverageTester.I.group()
        assert isinstance(result, str)
        assert result == "testing"
