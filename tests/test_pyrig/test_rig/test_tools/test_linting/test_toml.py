"""module."""

from pyrig.rig.tools.formatting.end_of_file import EndOfFileFormatter
from pyrig.rig.tools.linting.toml import TOMLLinter
from pyrig.rig.tools.typing.checker import TypeChecker


class TestTOMLLinter:
    """Test class."""

    def test_group(self) -> None:
        """Test method."""
        result = TOMLLinter.I.group()
        assert isinstance(result, str)
        assert result == "code-quality"

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            TOMLLinter.I.image_url()
            == "https://img.shields.io/badge/TOML-tombi-blueviolet"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert TOMLLinter.I.link_url() == "https://github.com/tombi-toml/tombi"

    def test_name(self) -> None:
        """Test method."""
        result = TOMLLinter.I.name()
        assert result == "tombi"

    def test_check_args(self) -> None:
        """Test method."""
        result = TOMLLinter.I.check_args()
        assert result == ("tombi", "lint")

    def test_format_args(self) -> None:
        """Test method."""
        result = TOMLLinter.I.format_args()
        assert result == ("tombi", "format")

    def test_check_hook(self) -> None:
        """Test method."""
        # ties into the checks tier rather than running after it
        hook = TOMLLinter.I.check_hook()
        types_hook = TypeChecker.I.check_hook()
        assert hook["priority"] == types_hook["priority"]
        assert hook["types"] == ["toml"]
        assert hook["exclude"] == TOMLLinter.I.lock_file_exclude_pattern()
        assert hook["args"] == ["--error-on-warnings"]

    def test_lint_toml(self) -> None:
        """Test method."""
        assert TOMLLinter.I.lint_toml() == TOMLLinter.I.check_args()

    def test_format_hook(self) -> None:
        """Test method."""
        # TOML formatting runs after the sequential text-fixing chain
        hook = TOMLLinter.I.format_hook()
        eof_hook = EndOfFileFormatter.I.format_hook()
        assert hook["priority"] > eof_hook["priority"]
        assert hook["types"] == ["toml"]
        assert hook["exclude"] == TOMLLinter.I.lock_file_exclude_pattern()

    def test_format_toml(self) -> None:
        """Test method."""
        assert TOMLLinter.I.format_toml() == TOMLLinter.I.format_args()

    def test_lock_file_exclude_pattern(self) -> None:
        """Test method."""
        assert TOMLLinter.I.lock_file_exclude_pattern() == "^uv\\.lock$"
