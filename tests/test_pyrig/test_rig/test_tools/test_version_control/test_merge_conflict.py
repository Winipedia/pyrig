"""module."""

from pyrig.rig.tools.typing.checker import TypeChecker
from pyrig.rig.tools.version_control.merge_conflict import MergeConflictChecker


class TestMergeConflictChecker:
    """Test class."""

    def test_group(self) -> None:
        """Test method."""
        result = MergeConflictChecker.I.group()
        assert isinstance(result, str)
        assert result == "code-quality"

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            MergeConflictChecker.I.image_url()
            == "https://img.shields.io/badge/merge--conflict-check--merge--conflict-blue"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert (
            MergeConflictChecker.I.link_url()
            == "https://github.com/pre-commit/pre-commit-hooks"
        )

    def test_name(self) -> None:
        """Test method."""
        result = MergeConflictChecker.I.name()
        assert result == "check-merge-conflict"

    def test_dev_dependencies(self) -> None:
        """Test method."""
        result = MergeConflictChecker.I.dev_dependencies()
        assert result == ("pre-commit-hooks",)

    def test_check_args(self) -> None:
        """Test method."""
        result = MergeConflictChecker.I.check_args()
        assert result == ("check-merge-conflict",)

    def test_check_hook(self) -> None:
        """Test method."""
        # ties into the checks tier rather than running after it
        hook = MergeConflictChecker.I.check_hook()
        types_hook = TypeChecker.I.check_hook()
        assert hook["priority"] == types_hook["priority"]
        assert hook["types"] == ["text"]

    def test_check_merge_conflict(self) -> None:
        """Test method."""
        assert (
            MergeConflictChecker.I.check_merge_conflict()
            == MergeConflictChecker.I.check_args()
        )
