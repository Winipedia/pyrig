"""module."""

from pytest_mock import MockerFixture

from pyrig.rig.tools.formatting.shell import ShellFormatter
from pyrig.rig.tools.linting.shell import ShellLinter


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

    def test_extension(self, mocker: MockerFixture) -> None:
        """Test method."""
        # Delegates to ShellLinter rather than coincidentally returning
        # the same literal, so patch it to prove that.
        mock = mocker.patch.object(
            ShellLinter,
            ShellLinter.extension.__name__,
            return_value="mocked-extension",
        )
        assert ShellFormatter.I.extension() == "mocked-extension"
        mock.assert_called_once()

    def test_regex(self) -> None:
        """Test method."""
        assert ShellFormatter.I.regex() == r"\.sh$"

    def test_format_args(self) -> None:
        """Test method."""
        result = ShellFormatter.I.format_args()
        assert result == ("shfmt", "-i", "2", "-ci", "-ln", "bash", "-w")
