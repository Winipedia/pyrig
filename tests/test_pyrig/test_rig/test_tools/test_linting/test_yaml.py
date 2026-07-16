"""module."""

from pyrig.rig.tools.formatting.end_of_file import EndOfFileFormatter
from pyrig.rig.tools.linting.yaml import YAMLLinter


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

    def test_version_control_hooks(self) -> None:
        """Test method."""
        assert YAMLLinter.I.version_control_hooks() == (YAMLLinter.I.check_hook(),)

    def test_check_hook(self) -> None:
        """Test method."""
        # YAML linting runs after the sequential text-fixing chain
        hook = YAMLLinter.I.check_hook()
        eof_hook = EndOfFileFormatter.I.format_hook()
        assert hook["priority"] > eof_hook["priority"]
        assert hook["types"] == ["yaml"]
        assert hook["args"] == ["--config-data=extends: default", "--fix"]

    def test_lint_yaml(self) -> None:
        """Test method."""
        assert YAMLLinter.I.lint_yaml() == YAMLLinter.I.check_args()
