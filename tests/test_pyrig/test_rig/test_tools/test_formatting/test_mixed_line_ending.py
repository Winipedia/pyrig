"""Test module."""

from pyrig.rig.tools.formatting.mixed_line_ending import MixedLineEndingFormatter
from pyrig.rig.tools.spelling.checker import SpellChecker


class TestMixedLineEndingFormatter:
    """Test class."""

    def test_group(self) -> None:
        """Test method."""
        result = MixedLineEndingFormatter.I.group()
        assert isinstance(result, str)
        assert result == "code-quality"

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            MixedLineEndingFormatter.I.image_url()
            == "https://img.shields.io/badge/EOL-mixed--line--ending-orange"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert (
            MixedLineEndingFormatter.I.link_url()
            == "https://github.com/pre-commit/pre-commit-hooks"
        )

    def test_name(self) -> None:
        """Test method."""
        result = MixedLineEndingFormatter.I.name()
        assert result == "mixed-line-ending"

    def test_dev_dependencies(self) -> None:
        """Test method."""
        result = MixedLineEndingFormatter.I.dev_dependencies()
        assert result == ("pre-commit-hooks",)

    def test_format_args(self) -> None:
        """Test method."""
        result = MixedLineEndingFormatter.I.format_args()
        assert result == ("mixed-line-ending",)

    def test_version_control_hooks(self) -> None:
        """Test method."""
        assert MixedLineEndingFormatter.I.version_control_hooks() == (
            MixedLineEndingFormatter.I.format_mixed_line_ending_hook(),
        )

    def test_format_mixed_line_ending_hook(self) -> None:
        """Test method."""
        # mixed line endings are normalized right after spelling is fixed,
        # so the later whitespace and end-of-file fixers never see a stray
        # carriage return left over from a non-LF line ending
        hook = MixedLineEndingFormatter.I.format_mixed_line_ending_hook()
        spelling_hook = SpellChecker.I.check_spelling_hook()
        assert hook["priority"] > spelling_hook["priority"]
        assert hook["types"] == ["text"]
        assert hook["args"] == ["--fix=lf"]

    def test_fix_mixed_line_ending(self) -> None:
        """Test method."""
        assert (
            MixedLineEndingFormatter.I.fix_mixed_line_ending()
            == MixedLineEndingFormatter.I.format_args()
        )
