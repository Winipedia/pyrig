"""module."""

from pyrig.rig.tools.formatting.end_of_file import EndOfFileFormatter
from pyrig.rig.tools.formatting.trailing_whitespace import TrailingWhitespaceFormatter


class TestEndOfFileFormatter:
    """Test class."""

    def test_group(self) -> None:
        """Test method."""
        result = EndOfFileFormatter.I.group()
        assert isinstance(result, str)
        assert result == "code-quality"

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            EndOfFileFormatter.I.image_url()
            == "https://img.shields.io/badge/EOF-end--of--file--fixer-orange"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert (
            EndOfFileFormatter.I.link_url()
            == "https://github.com/pre-commit/pre-commit-hooks"
        )

    def test_name(self) -> None:
        """Test method."""
        result = EndOfFileFormatter.I.name()
        assert result == "end-of-file-fixer"

    def test_dev_dependencies(self) -> None:
        """Test method."""
        result = EndOfFileFormatter.I.dev_dependencies()
        assert result == ()

    def test_format_args(self) -> None:
        """Test method."""
        result = EndOfFileFormatter.I.format_args()
        assert result == ()

    def test_format_hook(self) -> None:
        """Test method."""
        # the end-of-file fix runs last in the general text-fixing chain
        hook = EndOfFileFormatter.I.format_hook()
        whitespace_hook = TrailingWhitespaceFormatter.I.format_hook()
        assert hook["priority"] > whitespace_hook["priority"]

    def test_end_of_file_fixer(self) -> None:
        """Test method."""
        assert EndOfFileFormatter.I.end_of_file_fixer() == ()
