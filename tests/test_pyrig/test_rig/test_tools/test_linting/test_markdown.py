"""module."""

from pyrig.rig.tools.formatting.end_of_file import EndOfFileFormatter
from pyrig.rig.tools.linting.markdown import MarkdownLinter


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

    def test_version_control_hooks(self) -> None:
        """Test method."""
        assert MarkdownLinter.I.version_control_hooks() == (
            MarkdownLinter.I.check_markdown_hook(),
        )

    def test_check_markdown_hook(self) -> None:
        """Test method."""
        # Markdown linting runs after the sequential text-fixing chain
        hook = MarkdownLinter.I.check_markdown_hook()
        eof_hook = EndOfFileFormatter.I.format_end_of_file_hook()
        assert hook["priority"] > eof_hook["priority"]
        assert hook["types"] == ["markdown"]
        assert hook["args"] == ["--fix"]

    def test_lint_markdown(self) -> None:
        """Test method."""
        assert MarkdownLinter.I.lint_markdown() == MarkdownLinter.I.check_args()
