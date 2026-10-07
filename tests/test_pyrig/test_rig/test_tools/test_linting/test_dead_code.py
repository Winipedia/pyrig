"""Tests for the Vulture dead code checker wrapper."""

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.linting.dead_code import DeadCodeChecker
from pyrig.rig.tools.linting.python import PythonLinter
from pyrig.rig.tools.linting.toml import TOMLLinter
from pyrig.rig.tools.packages.manager import PackageManager


class TestDeadCodeChecker:
    """Test class."""

    def test_group(self) -> None:
        """Test method."""
        assert DeadCodeChecker.I.group() == "code-quality"

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            DeadCodeChecker.I.image_url()
            == "https://img.shields.io/badge/dead_code-vulture-blue"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert DeadCodeChecker.I.link_url() == "https://github.com/jendrikseipp/vulture"

    def test_name(self) -> None:
        """Test method."""
        assert DeadCodeChecker.I.name() == "vulture"
        assert DeadCodeChecker.I.dev_dependencies() == ("vulture",)

    def test_check_args(self) -> None:
        """Test method."""
        assert DeadCodeChecker.I.check_args() == Args("vulture")
        assert DeadCodeChecker.I.check_args("--verbose", "src") == Args(
            "vulture",
            "--verbose",
            "src",
        )

    def test_check_hook(self) -> None:
        """Test method."""
        hook = DeadCodeChecker.I.check_hook()
        assert hook["priority"] > PythonLinter.I.format_hook()["priority"]
        assert hook["priority"] > TOMLLinter.I.format_hook()["priority"]
        assert hook["types"] == ["python"]
        assert hook["pass_filenames"] is False
        assert hook["entry"] == str(DeadCodeChecker.I.check_dead_code())
        assert "args" not in hook
        assert DeadCodeChecker.I.hooks() == (hook,)

    def test_check_dead_code(self) -> None:
        """Test method."""
        assert DeadCodeChecker.I.check_dead_code() == PackageManager.I.run_args(
            *DeadCodeChecker.I.check_args(),
        )
