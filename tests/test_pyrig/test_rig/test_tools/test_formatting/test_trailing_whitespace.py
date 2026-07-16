"""module."""

from pyrig.rig.tools.formatting.trailing_whitespace import TrailingWhitespaceFormatter
from pyrig.rig.tools.language.spelling import SpellChecker


class TestTrailingWhitespaceFormatter:
    """Test class."""

    def test_group(self) -> None:
        """Test method."""
        result = TrailingWhitespaceFormatter.I.group()
        assert isinstance(result, str)
        assert result == "code-quality"

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            TrailingWhitespaceFormatter.I.image_url()
            == "https://img.shields.io/badge/whitespace-trailing--whitespace--fixer-orange"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert (
            TrailingWhitespaceFormatter.I.link_url()
            == "https://github.com/pre-commit/pre-commit-hooks"
        )

    def test_name(self) -> None:
        """Test method."""
        result = TrailingWhitespaceFormatter.I.name()
        assert result == "trailing-whitespace-fixer"

    def test_dev_dependencies(self) -> None:
        """Test method."""
        result = TrailingWhitespaceFormatter.I.dev_dependencies()
        assert result == ("pre-commit-hooks",)

    def test_format_args(self) -> None:
        """Test method."""
        result = TrailingWhitespaceFormatter.I.format_args()
        assert result == ("trailing-whitespace-fixer",)

    def test_version_control_hooks(self) -> None:
        """Test method."""
        assert TrailingWhitespaceFormatter.I.version_control_hooks() == (
            TrailingWhitespaceFormatter.I.format_trailing_whitespace_hook(),
        )

    def test_format_trailing_whitespace_hook(self) -> None:
        """Test method."""
        # trailing whitespace is fixed after spelling, so a spelling fix
        # can't reintroduce whitespace this hook already cleaned up
        hook = TrailingWhitespaceFormatter.I.format_trailing_whitespace_hook()
        spelling_hook = SpellChecker.I.check_spelling_hook()
        assert hook["priority"] > spelling_hook["priority"]
        assert hook["types"] == ["text"]

    def test_fix_trailing_whitespace(self) -> None:
        """Test method."""
        assert (
            TrailingWhitespaceFormatter.I.fix_trailing_whitespace()
            == TrailingWhitespaceFormatter.I.format_args()
        )
