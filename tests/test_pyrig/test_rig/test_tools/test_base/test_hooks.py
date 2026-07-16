"""Test module."""

from pyrig.rig.tools.base.hooks import VersionControlHookTool
from pyrig.rig.tools.formatting.end_of_file import EndOfFileFormatter
from pyrig.rig.tools.version_control.merge_conflict import MergeConflictChecker


class TestVersionControlHookTool:
    """Test class."""

    def test_hooks(self) -> None:
        """Test method."""
        # VersionControlHookTool is abstract, test through concrete implementation
        assert MergeConflictChecker.I.hooks() == (MergeConflictChecker.I.check_hook(),)

    def test_subclasses_hooks(self) -> None:
        """Test method."""
        hooks = list(VersionControlHookTool.subclasses_hooks())
        assert len(hooks) > 0
        assert all(isinstance(hook, dict) for hook in hooks)

    def test_sort_hooks(self) -> None:
        """Test method."""
        hooks = [
            {"stages": ["pre-commit"], "priority": 2, "id": "b"},
            {"stages": ["pre-commit"], "priority": 1, "id": "z"},
            {"stages": ["pre-commit"], "priority": 1, "id": "a"},
        ]
        sorted_hooks = VersionControlHookTool.sort_hooks(hooks)
        assert [hook["id"] for hook in sorted_hooks] == ["a", "z", "b"]


class TestCheckHookTool:
    """Test class."""

    def test_check_args(self) -> None:
        """Test method."""
        # CheckHookTool is abstract, test through concrete implementation
        result = MergeConflictChecker.I.check_args()
        assert result == ("check-merge-conflict",)

    def test_check_hook(self) -> None:
        """Test method."""
        hook = MergeConflictChecker.I.check_hook()
        assert isinstance(hook, dict)
        assert hook["id"] == "check-merge-conflict"

    def test_hooks(self) -> None:
        """Test method."""
        assert MergeConflictChecker.I.hooks() == (MergeConflictChecker.I.check_hook(),)


class TestFormatHookTool:
    """Test class."""

    def test_format_args(self) -> None:
        """Test method."""
        # FormatHookTool is abstract, test through concrete implementation
        result = EndOfFileFormatter.I.format_args()
        assert result == ("end-of-file-fixer",)

    def test_format_hook(self) -> None:
        """Test method."""
        hook = EndOfFileFormatter.I.format_hook()
        assert isinstance(hook, dict)
        assert hook["id"] == "fix-end-of-file"

    def test_hooks(self) -> None:
        """Test method."""
        assert EndOfFileFormatter.I.hooks() == (EndOfFileFormatter.I.format_hook(),)
