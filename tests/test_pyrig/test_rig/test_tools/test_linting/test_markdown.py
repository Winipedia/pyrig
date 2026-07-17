"""module."""

from pyrig.rig.tools.formatting.end_of_file import EndOfFileFormatter
from pyrig.rig.tools.linting.markdown import MarkdownLinter
from pyrig.rig.tools.packages.manager import PackageManager
from pyrig.rig.tools.typing.checker import TypeChecker


class TestMarkdownLinter:
    """Test class."""

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            MarkdownLinter.I.image_url()
            == "https://img.shields.io/badge/Markdown-rumdl-darkgreen"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert MarkdownLinter.I.link_url() == "https://github.com/rvben/rumdl"

    def test_version_control_ignore_patterns(self) -> None:
        """Test method."""
        assert MarkdownLinter.I.version_control_ignore_patterns() == (".rumdl_cache/",)

    def test_group(self) -> None:
        """Test method."""
        result = MarkdownLinter.I.group()
        assert isinstance(result, str)
        assert result == "code-quality"

    def test_name(self) -> None:
        """Test method."""
        result = MarkdownLinter.I.name()
        assert result == "rumdl"

    def test_check_args(self) -> None:
        """Test method."""
        result = MarkdownLinter.I.check_args()
        assert result == ("rumdl", "check")

    def test_check_hook(self) -> None:
        """Test method."""
        hook = MarkdownLinter.I.check_hook()
        type_check_hook = TypeChecker.I.check_hook()
        assert hook["priority"] == type_check_hook["priority"]
        assert hook["types"] == ["markdown"]

    def test_lint_markdown(self) -> None:
        """Test method."""
        base_args = MarkdownLinter.I.check_args()
        assert MarkdownLinter.I.lint_markdown() == PackageManager.I.run_args(*base_args)

    def test_format_args(self) -> None:
        """Test method."""
        result = MarkdownLinter.I.format_args()
        assert result == ("rumdl", "fmt")

    def test_format_hook(self) -> None:
        """Test method."""
        # Markdown formatting runs after the sequential text-fixing chain
        hook = MarkdownLinter.I.format_hook()
        eof_hook = EndOfFileFormatter.I.format_hook()
        assert hook["priority"] > eof_hook["priority"]
        assert hook["types"] == ["markdown"]

    def test_format_markdown(self) -> None:
        """Test method."""
        base_args = MarkdownLinter.I.format_args()
        assert MarkdownLinter.I.format_markdown() == PackageManager.I.run_args(
            *base_args,
        )
