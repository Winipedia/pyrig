"""Test module."""

from pyrig.rig.tools.formatting.end_of_line import EndOfLineFormatter
from pyrig.rig.tools.language.spelling import SpellChecker
from pyrig.rig.tools.packages.manager import PackageManager


class TestEndOfLineFormatter:
    """Test class."""

    def test_group(self) -> None:
        """Test method."""
        result = EndOfLineFormatter.I.group()
        assert isinstance(result, str)
        assert result == "code-quality"

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            EndOfLineFormatter.I.image_url()
            == "https://img.shields.io/badge/EOL-mixed--line--ending-orange"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert (
            EndOfLineFormatter.I.link_url()
            == "https://github.com/pre-commit/pre-commit-hooks"
        )

    def test_name(self) -> None:
        """Test method."""
        result = EndOfLineFormatter.I.name()
        assert result == "mixed-line-ending"

    def test_dev_dependencies(self) -> None:
        """Test method."""
        result = EndOfLineFormatter.I.dev_dependencies()
        assert result == ("pre-commit-hooks",)

    def test_format_args(self) -> None:
        """Test method."""
        result = EndOfLineFormatter.I.format_args()
        assert result == ("mixed-line-ending",)

    def test_format_hook(self) -> None:
        """Test method."""
        # mixed line endings are normalized right after spelling is fixed,
        # so the later whitespace and end-of-file fixers never see a stray
        # carriage return left over from a non-LF line ending
        hook = EndOfLineFormatter.I.format_hook()
        spelling_hook = SpellChecker.I.check_hook()
        assert hook["priority"] > spelling_hook["priority"]
        assert hook["types"] == ["text"]
        assert hook["args"] == ["--fix=lf"]

    def test_fix_end_of_line(self) -> None:
        """Test method."""
        base_args = EndOfLineFormatter.I.format_args()
        assert EndOfLineFormatter.I.fix_end_of_line() == PackageManager.I.run_args(
            *base_args,
        )
