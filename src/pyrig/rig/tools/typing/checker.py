"""Static type checker command construction and badge metadata."""

from typing import Any

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Group, Tool
from pyrig.rig.tools.linting.python import PythonLinter
from pyrig.rig.tools.version_control.hook_manager import VersionControlHookManager


class TypeChecker(Tool):
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

    def version_control_hooks(self) -> tuple[dict[str, Any], ...]:
        """Return the type checking hook.

        Returns:
            `check_types_hook`, wrapped in a single-element tuple.
        """
        return (self.check_types_hook(),)

    def check_types_hook(self) -> dict[str, Any]:
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
                PythonLinter.I.format_python_hook(),
            ),
            types=["python"],
            pass_filenames=False,
        )

    def check_types(self) -> Args:
        """Return the `Args` this hook's entry runs.

        Returns:
            Args for `ty check`.
        """
        return self.check_args()
