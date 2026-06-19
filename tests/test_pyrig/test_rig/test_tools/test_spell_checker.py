"""module."""

from pyrig.rig.tools import spell_checker
from pyrig.rig.tools.spell_checker import SpellChecker


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

    def test_check_fix_args(self) -> None:
        """Test method."""
        result = SpellChecker.I.check_fix_args()
        assert result == ("typos", "--write-changes")


def test_module_docstring() -> None:
    """Test module docstring."""
    assert (
        spell_checker.__doc__
        == """Spell checker tool wrapper.

Wraps SpellChecker commands and information.
"""
    )
