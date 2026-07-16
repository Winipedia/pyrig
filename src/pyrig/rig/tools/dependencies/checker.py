"""Detection of unused, missing, and transitive Python dependencies."""

from typing import Any

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.hooks import CheckHookTool
from pyrig.rig.tools.base.tool import Group
from pyrig.rig.tools.typing.checker import TypeChecker
from pyrig.rig.tools.version_control.hooks.manager import VersionControlHookManager


class DependencyChecker(CheckHookTool):
    """`deptry` command wrapper."""

    def group(self) -> str:
        """Return `Group.CODE_QUALITY`."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the Shields.io badge URL advertising `deptry`."""
        return f"https://img.shields.io/badge/dependencies-{self.shield_name()}-blue"

    def link_url(self) -> str:
        """Return the URL of the `deptry` project page."""
        return "https://github.com/osprey-oss/deptry"

    def name(self) -> str:
        """Return `"deptry"`."""
        return "deptry"

    def check_args(self, *args: str) -> Args:
        """Build the `deptry` command.

        Args:
            *args: Additional CLI flags for `deptry`.

        Returns:
            Args for running `deptry` with the given flags.
        """
        return self.args(*args)

    def check_hook(self) -> dict[str, Any]:
        """Return the hook metadata for detecting unused or missing dependencies.

        Ties its priority to `TypeChecker.check_hook` so it runs
        alongside the rest of the checks tier rather than after it.

        Returns:
            Hook metadata dict for `deptry`.
        """
        return VersionControlHookManager.I.hook(
            self.check_dependencies,
            priority=VersionControlHookManager.I.hook_priority(
                TypeChecker.I.check_hook(),
            ),
            types_or=["python", "pyproject"],
            pass_filenames=False,
        )

    def check_dependencies(self) -> Args:
        """Return the `Args` this hook's entry runs.

        Returns:
            Args for `deptry`.
        """
        return self.check_args()
