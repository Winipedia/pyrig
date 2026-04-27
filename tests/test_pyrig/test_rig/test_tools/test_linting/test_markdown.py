"""module."""

from pyrig.rig.tools.linting import markdown
from pyrig.rig.tools.linting.markdown import MarkdownLinter


class TestMarkdownLinter:
    """Test class."""

    def test_group(self) -> None:
        """Test method."""
        result = MarkdownLinter.I.group()
        assert isinstance(result, str)
        assert result == "code-quality"

    def test_badge_urls(self) -> None:
        """Test method."""
        result = MarkdownLinter.I.badge_urls()
        assert isinstance(result, tuple)
        assert all(isinstance(url, str) for url in result)

    def test_name(self) -> None:
        """Test method."""
        result = MarkdownLinter.I.name()
        assert result == "rumdl"

    def test_check_args(self) -> None:
        """Test method."""
        result = MarkdownLinter.I.check_args()
        assert result == ("rumdl", "check")

    def test_check_fix_args(self) -> None:
        """Test method."""
        result = MarkdownLinter.I.check_fix_args()
        assert result == ("rumdl", "check", "--fix")


def test_module_docstring() -> None:
    """Test module docstring."""
    assert (
        markdown.__doc__
        == """Wrapper around the Markdown PythonLinter tool.

Wraps Markdown PythonLinter commands and information.
"""
    )
