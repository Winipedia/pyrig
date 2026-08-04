"""Wrapper around the no-commit-to-branch tool."""

from typing import Any

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.hooks import CheckHookTool
from pyrig.rig.tools.base.tool import Group
from pyrig.rig.tools.packages.manager import PackageManager
from pyrig.rig.tools.typing.checker import TypeChecker
from pyrig.rig.tools.version_control.hooks.manager import VersionControlHookManager


class ProtectedBranchChecker(CheckHookTool):
    """Type-safe wrapper for the pre-commit-hooks protected branch checker."""

    def group(self) -> str:
        """Return `Group.CODE_QUALITY`, the badge group this tool belongs to."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the badge image URL for no-commit-to-branch."""
        return (
            f"https://img.shields.io/badge/protected--branch-{self.shield_name()}-blue"
        )

    def link_url(self) -> str:
        """Return the URL of the pre-commit-hooks project page."""
        return "https://github.com/pre-commit/pre-commit-hooks"

    def name(self) -> str:
        """Return `"no-commit-to-branch"`, this tool's CLI command name."""
        return "no-commit-to-branch"

    def dev_dependencies(self) -> tuple[str, ...]:
        """Return the package providing `no-commit-to-branch`."""
        return ("pre-commit-hooks",)

    def check_args(self, *args: str) -> Args:
        """Construct no-commit-to-branch arguments.

        Args:
            *args: Additional arguments forwarded to `no-commit-to-branch`.

        Returns:
            Args for `no-commit-to-branch`.
        """
        return self.args(*args)

    def check_hook(self) -> dict[str, Any]:
        """Return the hook metadata for blocking commits on a protected branch.

        Returns:
            Hook metadata dict for `no-commit-to-branch`.
        """
        return VersionControlHookManager.I.hook(
            self.check_protected_branch,
            priority=VersionControlHookManager.I.hook_priority(
                TypeChecker.I.check_hook(),
            ),
            always_run=True,
            pass_filenames=False,
        )

    def check_protected_branch(self) -> Args:
        """Return the `Args` this hook's entry runs.

        Returns:
            Args for `uv run no-commit-to-branch`.
        """
        return PackageManager.I.run_args(*self.check_args())
