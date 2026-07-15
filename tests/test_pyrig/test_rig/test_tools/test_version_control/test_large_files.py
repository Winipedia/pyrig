"""module."""

from pyrig.rig.tools.typing.checker import TypeChecker
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
        assert result == ("pre-commit-hooks",)

    def test_check_args(self) -> None:
        """Test method."""
        result = LargeFileChecker.I.check_args()
        assert result == ("check-added-large-files",)

    def test_version_control_hooks(self) -> None:
        """Test method."""
        assert LargeFileChecker.I.version_control_hooks() == (
            LargeFileChecker.I.check_large_files_hook(),
        )

    def test_check_large_files_hook(self) -> None:
        """Test method."""
        # ties into the checks tier rather than running after it
        hook = LargeFileChecker.I.check_large_files_hook()
        types_hook = TypeChecker.I.check_types_hook()
        assert hook["priority"] == types_hook["priority"]
        assert "types" not in hook

    def test_check_large_files(self) -> None:
        """Test method."""
        assert LargeFileChecker.I.check_large_files() == LargeFileChecker.I.check_args()
