"""Security scanner command construction and badge metadata."""

from typing import Any

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Group, Tool
from pyrig.rig.tools.testing.project import ProjectTester
from pyrig.rig.tools.typing.checker import TypeChecker
from pyrig.rig.tools.version_control.hook_manager import VersionControlHookManager


class SecurityLinter(Tool):
    """Wrapper for the `bandit` security checker.

    Constructs `bandit` command-line arguments for scanning source code for
    common security vulnerabilities.
    """

    def group(self) -> str:
        """Return `Group.CODE_QUALITY`."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the badge image URL for `bandit`."""
        return f"https://img.shields.io/badge/security-{self.shield_name()}-yellow.svg"

    def link_url(self) -> str:
        """Return the URL of the `bandit` project page."""
        return "https://github.com/PyCQA/bandit"

    def name(self) -> str:
        """Return `'bandit'`."""
        return "bandit"

    def check_args(self, *args: str) -> Args:
        """Construct `bandit` arguments.

        No target path is baked in: bandit silently skips a file it can't
        parse as Python rather than erroring, but still logs a warning and
        wastes a whole-tree walk doing so, so callers are expected to
        supply the specific files to check.

        Args:
            *args: Additional `bandit` arguments, typically the file paths
                to check.

        Returns:
            Args for `bandit [args]`.
        """
        return self.args(*args)

    def version_control_hooks(self) -> tuple[dict[str, Any], ...]:
        """Return the security scanning hook.

        Returns:
            `check_security_hook`, wrapped in a single-element tuple.
        """
        return (self.check_security_hook(),)

    def check_security_hook(self) -> dict[str, Any]:
        """Return the hook metadata for scanning Python source for vulnerabilities.

        Ties its priority to `TypeChecker.check_types_hook` so it runs
        alongside the rest of the checks tier rather than after it.

        Returns:
            Hook metadata dict for `bandit`.
        """
        return VersionControlHookManager.I.hook(
            self.check_security,
            priority=VersionControlHookManager.I.hook_priority(
                TypeChecker.I.check_types_hook(),
            ),
            types=["python"],
            args=[
                "--exclude",
                ProjectTester.I.package_root().as_posix(),
            ],
        )

    def check_security(self) -> Args:
        """Return the `Args` this hook's entry runs.

        Returns:
            Args for `bandit`.
        """
        return self.check_args()
