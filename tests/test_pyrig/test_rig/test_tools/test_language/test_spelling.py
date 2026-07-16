"""module."""

from pyrig.rig.tools.formatting.byte_order_marker import ByteOrderMarkerFormatter
from pyrig.rig.tools.language.spelling import SpellChecker


class TestSpellChecker:
    """Test class."""

    def test_name(self) -> None:
        """Test method."""
        assert SpellChecker.I.name() == "typos"

    def test_group(self) -> None:
        """Test method."""
        result = SpellChecker.I.group()
        assert isinstance(result, str)
        assert result == "code-quality"

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            SpellChecker.I.image_url()
            == "https://img.shields.io/badge/spell--check-typos-blue"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert SpellChecker.I.link_url() == "https://github.com/crate-ci/typos"

    def test_check_args(self) -> None:
        """Test method."""
        result = SpellChecker.I.check_args()
        assert result == ("typos",)

    def test_check_hook(self) -> None:
        """Test method."""
        # spelling is checked right after the byte-order marker is stripped
        hook = SpellChecker.I.check_hook()
        bom_hook = ByteOrderMarkerFormatter.I.format_hook()
        assert hook["priority"] > bom_hook["priority"]
        assert hook["types"] == ["text"]
        assert hook["args"] == ["--write-changes"]

    def test_fix_spelling(self) -> None:
        """Test method."""
        assert SpellChecker.I.fix_spelling() == SpellChecker.I.check_args()
