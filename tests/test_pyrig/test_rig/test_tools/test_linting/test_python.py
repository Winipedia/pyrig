"""module."""

from pyrig.rig.tools.formatting.end_of_file import EndOfFileFormatter
from pyrig.rig.tools.linting.python import PythonLinter


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

    def test_version_control_hooks(self) -> None:
        """Test method."""
        assert PythonLinter.I.version_control_hooks() == (
            PythonLinter.I.check_hook(),
            PythonLinter.I.format_hook(),
        )

    def test_check_hook(self) -> None:
        """Test method."""
        # Python linting runs after the sequential text-fixing chain
        hook = PythonLinter.I.check_hook()
        eof_hook = EndOfFileFormatter.I.format_hook()
        assert hook["priority"] > eof_hook["priority"]
        assert hook["types"] == ["python"]
        assert hook["args"] == ["--fix"]

    def test_lint_python(self) -> None:
        """Test method."""
        assert PythonLinter.I.lint_python() == PythonLinter.I.check_args()

    def test_format_hook(self) -> None:
        """Test method."""
        # formatting runs after linting, so it never fights ruff's own fixes
        format_hook = PythonLinter.I.format_hook()
        check_hook = PythonLinter.I.check_hook()
        assert format_hook["priority"] > check_hook["priority"]
        assert format_hook["types"] == ["python"]

    def test_format_python(self) -> None:
        """Test method."""
        assert PythonLinter.I.format_python() == PythonLinter.I.format_args()
