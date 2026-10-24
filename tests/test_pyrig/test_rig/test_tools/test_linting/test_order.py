"""Tests for the Python source order linter wrapper."""

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.hooks import VersionControlHookTool
from pyrig.rig.tools.base.tool import Tool
from pyrig.rig.tools.linting.order import PythonOrderLinter
from pyrig.rig.tools.linting.python import PythonLinter
from pyrig.rig.tools.packages.manager import PackageManager
from pyrig.rig.tools.security.secrets import SecretsChecker


class TestPythonOrderLinter:
    """Test class."""

    def test_group(self) -> None:
        """Test method."""
        assert PythonOrderLinter.I.group() == "code-quality"

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            PythonOrderLinter.I.image_url()
            == "https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/Winipedia/pyorder/main/docs/assets/badge.json"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert PythonOrderLinter.I.link_url() == "https://github.com/Winipedia/pyorder"

    def test_name(self) -> None:
        """Test method."""
        assert PythonOrderLinter.I.name() == "pyorder"
        assert PythonOrderLinter.I.dev_dependencies() == ("pyorder",)
        assert "pyorder" in Tool.subclasses_dev_dependencies()

    def test_check_args(self) -> None:
        """Test method."""
        assert PythonOrderLinter.I.check_args() == Args("pyorder", "check")
        assert PythonOrderLinter.I.check_args("--fix", "example.py") == Args(
            "pyorder",
            "check",
            "--fix",
            "example.py",
        )

    def test_check_hook(self) -> None:
        """Test method."""
        hook = PythonOrderLinter.I.check_hook()
        assert hook["priority"] > SecretsChecker.I.check_hook()["priority"]
        assert hook["priority"] < PythonLinter.I.check_hook()["priority"]
        assert hook["priority"] < PythonLinter.I.format_hook()["priority"]
        assert hook["id"] == "lint-python-order"
        assert hook["entry"] == str(PythonOrderLinter.I.lint_python_order())
        assert hook["language"] == "system"
        assert hook["types"] == ["python"]
        assert hook["args"] == ["--fix"]
        assert hook["stages"] == ["pre-commit"]
        assert "pass_filenames" not in hook
        assert PythonOrderLinter.I.hooks() == (hook,)
        assert hook in VersionControlHookTool.subclasses_hooks()

    def test_lint_python_order(self) -> None:
        """Test method."""
        assert PythonOrderLinter.I.lint_python_order() == PackageManager.I.run_args(
            *PythonOrderLinter.I.check_args(),
        )
