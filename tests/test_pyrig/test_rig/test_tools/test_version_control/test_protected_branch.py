"""module."""

from pyrig.rig.tools.packages.manager import PackageManager
from pyrig.rig.tools.typing.checker import TypeChecker
from pyrig.rig.tools.version_control.protected_branch import ProtectedBranchChecker


class TestProtectedBranchChecker:
    """Test class."""

    def test_group(self) -> None:
        """Test method."""
        result = ProtectedBranchChecker.I.group()
        assert isinstance(result, str)
        assert result == "code-quality"

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            ProtectedBranchChecker.I.image_url()
            == "https://img.shields.io/badge/protected--branch-no--commit--to--branch-blue"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert (
            ProtectedBranchChecker.I.link_url()
            == "https://github.com/pre-commit/pre-commit-hooks"
        )

    def test_name(self) -> None:
        """Test method."""
        result = ProtectedBranchChecker.I.name()
        assert result == "no-commit-to-branch"

    def test_dev_dependencies(self) -> None:
        """Test method."""
        result = ProtectedBranchChecker.I.dev_dependencies()
        assert result == ("pre-commit-hooks",)

    def test_check_args(self) -> None:
        """Test method."""
        result = ProtectedBranchChecker.I.check_args()
        assert result == ("no-commit-to-branch",)

    def test_check_hook(self) -> None:
        """Test method."""
        # ties into the checks tier rather than running after it
        hook = ProtectedBranchChecker.I.check_hook()
        types_hook = TypeChecker.I.check_hook()
        assert hook["priority"] == types_hook["priority"]
        assert hook["always_run"] is True
        assert hook["pass_filenames"] is False

    def test_check_protected_branch(self) -> None:
        """Test method."""
        base_args = ProtectedBranchChecker.I.check_args()
        assert (
            ProtectedBranchChecker.I.check_protected_branch()
            == PackageManager.I.run_args(*base_args)
        )
