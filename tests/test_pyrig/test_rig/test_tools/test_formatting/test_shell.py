"""module."""

from pyrig.rig.tools.formatting.end_of_file import EndOfFileFormatter
from pyrig.rig.tools.formatting.shell import ShellFormatter


class TestShellFormatter:
    """Test class."""

    def test_group(self) -> None:
        """Test method."""
        result = ShellFormatter.I.group()
        assert isinstance(result, str)
        assert result == "code-quality"

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            ShellFormatter.I.image_url()
            == "https://img.shields.io/badge/shell-shfmt-orange"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert ShellFormatter.I.link_url() == "https://github.com/mvdan/sh"

    def test_name(self) -> None:
        """Test method."""
        result = ShellFormatter.I.name()
        assert result == "shfmt"

    def test_dev_dependencies(self) -> None:
        """Test method."""
        result = ShellFormatter.I.dev_dependencies()
        assert result == ("shfmt-py",)

    def test_format_args(self) -> None:
        """Test method."""
        result = ShellFormatter.I.format_args()
        assert result == ("shfmt",)

    def test_version_control_hooks(self) -> None:
        """Test method."""
        assert ShellFormatter.I.version_control_hooks() == (
            ShellFormatter.I.format_hook(),
        )

    def test_format_hook(self) -> None:
        """Test method."""
        # shell formatting runs after the sequential text-fixing chain
        hook = ShellFormatter.I.format_hook()
        eof_hook = EndOfFileFormatter.I.format_hook()
        assert hook["priority"] > eof_hook["priority"]
        assert hook["types"] == ["shell"]

    def test_format_shell(self) -> None:
        """Test method."""
        assert ShellFormatter.I.format_shell() == ShellFormatter.I.format_args()
