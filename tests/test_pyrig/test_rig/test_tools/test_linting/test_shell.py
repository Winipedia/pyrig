"""module."""

from pyrig.rig.tools.linting.shell import ShellLinter
from pyrig.rig.tools.typing.checker import TypeChecker


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

    def test_lint_args(self) -> None:
        """Test method."""
        result = ShellLinter.I.lint_args()
        assert result == ("shellcheck",)

    def test_version_control_hooks(self) -> None:
        """Test method."""
        assert ShellLinter.I.version_control_hooks() == (
            ShellLinter.I.lint_shell_hook(),
        )

    def test_lint_shell_hook(self) -> None:
        """Test method."""
        # ties into the checks tier rather than running after it
        hook = ShellLinter.I.lint_shell_hook()
        types_hook = TypeChecker.I.check_types_hook()
        assert hook["priority"] == types_hook["priority"]
        assert hook["types"] == ["shell"]

    def test_lint_shell(self) -> None:
        """Test method."""
        assert ShellLinter.I.lint_shell() == ShellLinter.I.lint_args()
