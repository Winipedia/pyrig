"""module."""

from pyrig.rig.tools.linting.yaml import YAMLLinter
from pyrig.rig.tools.packages.manager import PackageManager
from pyrig.rig.tools.security.secrets import SecretsChecker


class TestYAMLLinter:
    """Test class."""

    def test_image_url(self) -> None:
        """Test method."""
        assert YAMLLinter.I.image_url() == "https://img.shields.io/badge/YAML-ryl-red"

    def test_link_url(self) -> None:
        """Test method."""
        assert YAMLLinter.I.link_url() == "https://github.com/owenlamont/ryl"

    def test_group(self) -> None:
        """Test method."""
        result = YAMLLinter.I.group()
        assert isinstance(result, str)
        assert result == "code-quality"

    def test_name(self) -> None:
        """Test method."""
        result = YAMLLinter.I.name()
        assert result == "ryl"

    def test_check_args(self) -> None:
        """Test method."""
        result = YAMLLinter.I.check_args()
        assert result == ("ryl", "check")

    def test_check_hook(self) -> None:
        """Test method."""
        # YAML fixing runs after the general read-only checks
        hook = YAMLLinter.I.check_hook()
        secrets_hook = SecretsChecker.I.check_hook()
        assert hook["priority"] > secrets_hook["priority"]
        assert hook["types"] == ["yaml"]
        assert hook["args"] == [
            "--fix",
            "--strict",
        ]

    def test_lint_yaml(self) -> None:
        """Test method."""
        base_args = YAMLLinter.I.check_args()
        assert YAMLLinter.I.lint_yaml() == PackageManager.I.run_args(*base_args)

    def test_disable_line_line_length(self) -> None:
        """Test method."""
        assert (
            YAMLLinter.I.disable_line_line_length()
            == "# ryl disable-line rule:line-length"
        )

    def test_disable_line(self) -> None:
        """Test method."""
        directive = YAMLLinter.I.disable_line("some-rule")
        assert directive == "# ryl disable-line rule:some-rule"

    def test_directive(self) -> None:
        """Test method."""
        directive = YAMLLinter.I.directive("some_directive")
        assert directive == "# ryl some_directive"
