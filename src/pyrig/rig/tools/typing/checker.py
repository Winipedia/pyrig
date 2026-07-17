"""Static type checker command construction and badge metadata."""

from typing import Any

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.hooks import CheckHookTool
from pyrig.rig.tools.base.tool import Group
from pyrig.rig.tools.linting.python import PythonLinter
from pyrig.rig.tools.packages.manager import PackageManager
from pyrig.rig.tools.version_control.hooks.manager import VersionControlHookManager


class TypeChecker(CheckHookTool):
    """Type-safe wrapper for the `ty` static type checker."""

    def group(self) -> str:
        """Return `Group.CODE_QUALITY`."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the badge image URL for `ty`."""
        return "https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json"

    def link_url(self) -> str:
        """Return the URL of the `ty` project page."""
        return "https://github.com/astral-sh/ty"

    def name(self) -> str:
        """Return `'ty'`."""
        return "ty"

    def check_args(self, *args: str) -> Args:
        """Build the command for running `ty check`.

        Args:
            *args: Additional arguments appended after `check`.

        Returns:
            Args for `ty check [args]`.
        """
        return self.args("check", *args)

    def check_hook(self) -> dict[str, Any]:
        """Return the hook metadata for type checking Python source.

        Anchors the checks tier: it runs after Python formatting, and every
        other check ties its own priority to this one via `hook_priority`
        rather than each picking its own, so the whole tier runs together.

        Returns:
            Hook metadata dict for `ty check`.
        """
        return VersionControlHookManager.I.hook(
            self.check_types,
            priority=VersionControlHookManager.I.increase_priority(
                PythonLinter.I.format_hook(),
            ),
            types=["python"],
            pass_filenames=False,
        )

    def check_types(self) -> Args:
        """Return the `Args` this hook's entry runs.

        Returns:
            Args for `uv run ty check`.
        """
        return PackageManager.I.run_args(*self.check_args())
