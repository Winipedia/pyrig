"""module."""

from pyrig.rig.tools.linting.toml import TOMLLinter
from pyrig.rig.tools.packages.manager import PackageManager
from pyrig.rig.tools.security.secrets import SecretsChecker


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
        # TOML linting runs after TOML formatting
        hook = TOMLLinter.I.check_hook()
        format_hook = TOMLLinter.I.format_hook()
        assert hook["priority"] > format_hook["priority"]
        assert hook["types"] == ["toml"]
        assert hook["exclude"] == TOMLLinter.I.lock_file_exclude_pattern()
        assert hook["args"] == ["--error-on-warnings"]

    def test_lint_toml(self) -> None:
        """Test method."""
        base_args = TOMLLinter.I.check_args()
        assert TOMLLinter.I.lint_toml() == PackageManager.I.run_args(*base_args)

    def test_format_hook(self) -> None:
        """Test method."""
        # TOML formatting runs after the general read-only checks
        hook = TOMLLinter.I.format_hook()
        secrets_hook = SecretsChecker.I.check_hook()
        assert hook["priority"] > secrets_hook["priority"]
        assert hook["types"] == ["toml"]
        assert hook["exclude"] == TOMLLinter.I.lock_file_exclude_pattern()

    def test_format_toml(self) -> None:
        """Test method."""
        base_args = TOMLLinter.I.format_args()
        assert TOMLLinter.I.format_toml() == PackageManager.I.run_args(*base_args)

    def test_lock_file_exclude_pattern(self) -> None:
        """Test method."""
        assert TOMLLinter.I.lock_file_exclude_pattern() == "^uv\\.lock$"
