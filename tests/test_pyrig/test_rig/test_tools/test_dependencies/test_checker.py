"""Test module."""

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.dependencies.checker import DependencyChecker
from pyrig.rig.tools.linting.python import PythonLinter
from pyrig.rig.tools.linting.toml import TOMLLinter
from pyrig.rig.tools.packages.manager import PackageManager


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

    def test_check_hook(self) -> None:
        """Test method."""
        # dependency checking runs after Python formatting and linting,
        # and TOML formatting
        hook = DependencyChecker.I.check_hook()
        format_hook = PythonLinter.I.format_hook()
        python_hook = PythonLinter.I.check_hook()
        toml_hook = TOMLLinter.I.format_hook()
        assert hook["priority"] > format_hook["priority"]
        assert hook["priority"] > python_hook["priority"]
        assert hook["priority"] > toml_hook["priority"]
        assert hook["types_or"] == ["pyproject", "python"]
        assert hook["pass_filenames"] is False

    def test_check_dependencies(self) -> None:
        """Test method."""
        assert DependencyChecker.I.check_dependencies() == PackageManager.I.run_args(
            *DependencyChecker.I.check_args(),
        )
