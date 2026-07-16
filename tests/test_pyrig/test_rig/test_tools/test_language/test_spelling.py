"""module."""

from pyrig.rig.tools.language.spelling import SpellChecker
from pyrig.rig.tools.pyrigger import Pyrigger


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

    def test_version_control_hooks(self) -> None:
        """Test method."""
        assert SpellChecker.I.version_control_hooks() == (
            SpellChecker.I.check_spelling_hook(),
        )

    def test_check_spelling_hook(self) -> None:
        """Test method."""
        # spelling is checked after the project has been synchronized
        hook = SpellChecker.I.check_spelling_hook()
        sync_hook = Pyrigger.I.synchronize_project_hook()
        assert hook["priority"] > sync_hook["priority"]
        assert hook["types"] == ["text"]
        assert hook["args"] == ["--write-changes"]

    def test_fix_spelling(self) -> None:
        """Test method."""
        assert SpellChecker.I.fix_spelling() == SpellChecker.I.check_args()
