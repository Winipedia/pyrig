"""module."""

from pyrig.rig.tools.language.case_conflict import CaseConflictChecker
from pyrig.rig.tools.packages.manager import PackageManager
from pyrig.rig.tools.typing.checker import TypeChecker


class TestCaseConflictChecker:
    """Test class."""

    def test_group(self) -> None:
        """Test method."""
        result = CaseConflictChecker.I.group()
        assert isinstance(result, str)
        assert result == "code-quality"

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            CaseConflictChecker.I.image_url()
            == "https://img.shields.io/badge/case--conflict-check--case--conflict-blue"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert (
            CaseConflictChecker.I.link_url()
            == "https://github.com/pre-commit/pre-commit-hooks"
        )

    def test_name(self) -> None:
        """Test method."""
        result = CaseConflictChecker.I.name()
        assert result == "check-case-conflict"

    def test_dev_dependencies(self) -> None:
        """Test method."""
        result = CaseConflictChecker.I.dev_dependencies()
        assert result == ("pre-commit-hooks",)

    def test_check_args(self) -> None:
        """Test method."""
        result = CaseConflictChecker.I.check_args()
        assert result == ("check-case-conflict",)

    def test_check_hook(self) -> None:
        """Test method."""
        # ties into the checks tier rather than running after it
        hook = CaseConflictChecker.I.check_hook()
        types_hook = TypeChecker.I.check_hook()
        assert hook["priority"] == types_hook["priority"]
        assert "types" not in hook

    def test_check_case_conflict(self) -> None:
        """Test method."""
        base_args = CaseConflictChecker.I.check_args()
        assert CaseConflictChecker.I.check_case_conflict() == PackageManager.I.run_args(
            *base_args,
        )
