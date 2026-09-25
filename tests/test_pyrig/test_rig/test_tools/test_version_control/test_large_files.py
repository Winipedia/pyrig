"""module."""

from pyrig.rig.tools.formatting.end_of_file import EndOfFileFormatter
from pyrig.rig.tools.version_control.large_files import LargeFileChecker


class TestLargeFileChecker:
    """Test class."""

    def test_group(self) -> None:
        """Test method."""
        result = LargeFileChecker.I.group()
        assert isinstance(result, str)
        assert result == "code-quality"

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            LargeFileChecker.I.image_url()
            == "https://img.shields.io/badge/large--files-check--added--large--files-blue"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert (
            LargeFileChecker.I.link_url()
            == "https://github.com/pre-commit/pre-commit-hooks"
        )

    def test_name(self) -> None:
        """Test method."""
        result = LargeFileChecker.I.name()
        assert result == "check-added-large-files"

    def test_dev_dependencies(self) -> None:
        """Test method."""
        result = LargeFileChecker.I.dev_dependencies()
        assert result == ()

    def test_check_args(self) -> None:
        """Test method."""
        result = LargeFileChecker.I.check_args()
        assert result == ("--enforce-all",)

    def test_check_hook(self) -> None:
        """Test method."""
        # large-file checking runs after the general text-fixing chain
        hook = LargeFileChecker.I.check_hook()
        eof_hook = EndOfFileFormatter.I.format_hook()
        assert hook["priority"] > eof_hook["priority"]
        assert "types" not in hook
        assert hook["args"] == ["--enforce-all"]

    def test_check_added_large_files(self) -> None:
        """Test method."""
        assert LargeFileChecker.I.check_added_large_files() == ("--enforce-all",)
