"""module."""

from pyrig.rig.tools.formatting.end_of_file import EndOfFileFormatter
from pyrig.rig.tools.linting.markdown import MarkdownLinter
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

    def test_lint_args(self) -> None:
        """Test method."""
        result = MarkdownLinter.I.lint_args()
        assert result == ("rumdl", "check")

    def test_version_control_hooks(self) -> None:
        """Test method."""
        assert MarkdownLinter.I.version_control_hooks() == (
            MarkdownLinter.I.lint_markdown_hook(),
            MarkdownLinter.I.format_markdown_hook(),
        )

    def test_lint_markdown_hook(self) -> None:
        """Test method."""
        hook = MarkdownLinter.I.lint_markdown_hook()
        type_check_hook = TypeChecker.I.check_types_hook()
        assert hook["priority"] == type_check_hook["priority"]
        assert hook["types"] == ["markdown"]

    def test_lint_markdown(self) -> None:
        """Test method."""
        assert MarkdownLinter.I.lint_markdown() == MarkdownLinter.I.lint_args()

    def test_format_args(self) -> None:
        """Test method."""
        result = MarkdownLinter.I.format_args()
        assert result == ("rumdl", "fmt")

    def test_format_markdown_hook(self) -> None:
        """Test method."""
        # Markdown formatting runs after the sequential text-fixing chain
        hook = MarkdownLinter.I.format_markdown_hook()
        eof_hook = EndOfFileFormatter.I.format_end_of_file_hook()
        assert hook["priority"] > eof_hook["priority"]
        assert hook["types"] == ["markdown"]

    def test_format_markdown(self) -> None:
        """Test method."""
        assert MarkdownLinter.I.format_markdown() == MarkdownLinter.I.format_args()
