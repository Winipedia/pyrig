"""CLI tool wrapper for spell checking source code and documentation."""

from typing import Any

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Group, Tool
from pyrig.rig.tools.pyrigger import Pyrigger
from pyrig.rig.tools.version_control.hook_manager import VersionControlHookManager


class SpellChecker(Tool):
    """Wrapper for the `typos` spell checker.

    Constructs `typos` command-line arguments for detecting and fixing
    spelling mistakes in source code, comments, and documentation.
    """

    def group(self) -> str:
        """Return `Group.CODE_QUALITY`."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the badge image URL for `typos`."""
        return f"https://img.shields.io/badge/spell--check-{self.shield_name()}-blue"

    def link_url(self) -> str:
        """Return the URL of the `typos` project page."""
        return "https://github.com/crate-ci/typos"

    def name(self) -> str:
        """Return `'typos'`."""
        return "typos"

    def check_args(self, *args: str) -> Args:
        """Construct `typos` arguments for checking without fixing.

        Args:
            *args: Additional arguments forwarded to `typos`.

        Returns:
            Args for `typos [args]`.
        """
        return self.args(*args)

    def version_control_hooks(self) -> tuple[dict[str, Any], ...]:
        """Return the spelling hook.

        Returns:
            `check_spelling_hook`, wrapped in a single-element tuple.
        """
        return (self.check_spelling_hook(),)

    def check_spelling_hook(self) -> dict[str, Any]:
        """Return the hook metadata for fixing spelling mistakes.

        Runs after project synchronization, since syncing can create or
        update the files this hook then spell-checks.

        Returns:
            Hook metadata dict for `typos --write-changes`.
        """
        return VersionControlHookManager.I.hook(
            self.fix_spelling,
            priority=VersionControlHookManager.I.increase_priority(
                Pyrigger.I.synchronize_project_hook(),
            ),
            types=["text"],
            args=["--write-changes"],
        )

    def fix_spelling(self) -> Args:
        """Return the `Args` this hook's entry runs.

        Returns:
            Args for `typos --write-changes`.
        """
        return self.check_args()
