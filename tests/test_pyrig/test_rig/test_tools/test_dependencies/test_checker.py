"""Test module."""

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.dependencies.checker import DependencyChecker


class TestDependencyChecker:
    """Test class."""

    def test_check_args(self) -> None:
        """Test method."""
        assert DependencyChecker.I.check_args() == Args(("deptry",))

    def test_name(self) -> None:
        """Test method."""
        assert DependencyChecker.I.name() == "deptry"

    def test_group(self) -> None:
        """Test method."""
        assert DependencyChecker.I.group() == "code-quality"

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            DependencyChecker.I.image_url()
            == "https://img.shields.io/badge/dependencies-deptry-blue"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert DependencyChecker.I.link_url() == "https://github.com/osprey-oss/deptry"
