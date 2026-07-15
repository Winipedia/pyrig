"""Test module."""

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.dependencies.checker import DependencyChecker
from pyrig.rig.tools.typing.checker import TypeChecker


class TestDependencyChecker:
    """Test class."""

    def test_check_args(self) -> None:
        """Test method."""
        assert DependencyChecker.I.check_args() == Args("deptry")

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

    def test_version_control_hooks(self) -> None:
        """Test method."""
        assert DependencyChecker.I.version_control_hooks() == (
            DependencyChecker.I.check_dependencies_hook(),
        )

    def test_check_dependencies_hook(self) -> None:
        """Test method."""
        # ties into the checks tier rather than running after it
        hook = DependencyChecker.I.check_dependencies_hook()
        types_hook = TypeChecker.I.check_types_hook()
        assert hook["priority"] == types_hook["priority"]
        assert hook["types_or"] == ["pyproject", "python"]
        assert hook["pass_filenames"] is False

    def test_check_dependencies(self) -> None:
        """Test method."""
        assert (
            DependencyChecker.I.check_dependencies() == DependencyChecker.I.check_args()
        )
