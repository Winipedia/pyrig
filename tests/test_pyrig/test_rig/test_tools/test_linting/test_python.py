"""module."""

from pyrig.rig.tools.linting.markdown import MarkdownLinter
from pyrig.rig.tools.linting.python import PythonLinter
from pyrig.rig.tools.packages.manager import PackageManager
from pyrig.rig.tools.security.secrets import SecretsChecker


class TestPythonLinter:
    """Test class."""

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            PythonLinter.I.image_url()
            == "https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert PythonLinter.I.link_url() == "https://github.com/astral-sh/ruff"

    def test_version_control_ignore_patterns(self) -> None:
        """Test method."""
        assert PythonLinter.I.version_control_ignore_patterns() == (".ruff_cache/",)

    def test_pydocstyle(self) -> None:
        """Test method."""
        assert PythonLinter.I.pydocstyle() == "google"

    def test_group(self) -> None:
        """Test method."""
        result = PythonLinter.I.group()
        assert isinstance(result, str)
        assert result == "code-quality"

    def test_name(self) -> None:
        """Test method."""
        result = PythonLinter.I.name()
        assert result == "ruff"

    def test_check_args(self) -> None:
        """Test method."""
        result = PythonLinter.I.check_args()
        assert result == ("ruff", "check")

    def test_format_args(self) -> None:
        """Test method."""
        result = PythonLinter.I.format_args()
        assert result == ("ruff", "format")

    def test_check_hook(self) -> None:
        """Test method."""
        # Ruff formatting runs after Ruff's autofixing linter
        hook = PythonLinter.I.check_hook()
        format_hook = PythonLinter.I.format_hook()
        assert format_hook["priority"] > hook["priority"]
        assert hook["types"] == ["python"]
        assert hook["args"] == ["--fix"]

    def test_lint_python(self) -> None:
        """Test method."""
        assert PythonLinter.I.lint_python() == PackageManager.I.run_args(
            *PythonLinter.I.check_args(),
        )

    def test_format_hook(self) -> None:
        """Test method."""
        # Ruff formatting runs after the general checks
        format_hook = PythonLinter.I.format_hook()
        secrets_hook = SecretsChecker.I.check_hook()
        assert format_hook["priority"] > secrets_hook["priority"]
        markdown_hook = MarkdownLinter.I.format_hook()
        assert markdown_hook["priority"] < format_hook["priority"]
        assert format_hook["types_or"] == ["markdown", "python"]

    def test_format_python(self) -> None:
        """Test method."""
        assert PythonLinter.I.format_python() == PackageManager.I.run_args(
            *PythonLinter.I.format_args(),
        )
