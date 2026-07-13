"""module."""

from pyrig.rig.tools.linting.shell import ShellLinter


class TestShellLinter:
    """Test class."""

    def test_group(self) -> None:
        """Test method."""
        result = ShellLinter.I.group()
        assert isinstance(result, str)
        assert result == "code-quality"

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            ShellLinter.I.image_url()
            == "https://img.shields.io/badge/shell-shellcheck-blue"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert ShellLinter.I.link_url() == "https://github.com/koalaman/shellcheck"

    def test_name(self) -> None:
        """Test method."""
        result = ShellLinter.I.name()
        assert result == "shellcheck"

    def test_dev_dependencies(self) -> None:
        """Test method."""
        result = ShellLinter.I.dev_dependencies()
        assert result == ("shellcheck-py",)

    def test_types(self) -> None:
        """Test method."""
        assert ShellLinter.I.types() == ["shell"]

    def test_check_args(self) -> None:
        """Test method."""
        result = ShellLinter.I.check_args()
        assert result == (
            "shellcheck",
            "--severity=style",
            "--enable=all",
            "--shell=bash",
        )
