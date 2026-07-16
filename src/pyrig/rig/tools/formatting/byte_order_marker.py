"""Wrapper around the fix-byte-order-marker tool."""

from typing import Any

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Group, Tool
from pyrig.rig.tools.pyrigger import Pyrigger
from pyrig.rig.tools.version_control.hooks.manager import VersionControlHookManager


class ByteOrderMarkerFormatter(Tool):
    """Type-safe wrapper for the pre-commit-hooks byte-order-marker fixer."""

    def group(self) -> str:
        """Return `Group.CODE_QUALITY`, the badge group this tool belongs to."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the badge image URL for fix-byte-order-marker."""
        return f"https://img.shields.io/badge/BOM-{self.shield_name()}-orange"

    def link_url(self) -> str:
        """Return the URL of the pre-commit-hooks project page."""
        return "https://github.com/pre-commit/pre-commit-hooks"

    def name(self) -> str:
        """Return `"fix-byte-order-marker"`, this tool's CLI command name."""
        return "fix-byte-order-marker"

    def dev_dependencies(self) -> tuple[str, ...]:
        """Return the package providing `fix-byte-order-marker`."""
        return ("pre-commit-hooks",)

    def format_args(self, *args: str) -> Args:
        """Construct fix-byte-order-marker arguments.

        Like `trailing-whitespace-fixer`, this tool has no separate autofix
        flag: it always strips a leading byte-order mark in place and
        reports via its exit code whether anything changed.

        Args:
            *args: Additional arguments forwarded to `fix-byte-order-marker`,
                typically the file paths to fix.

        Returns:
            Args for `fix-byte-order-marker`.
        """
        return self.args(*args)

    def version_control_hooks(self) -> tuple[dict[str, Any], ...]:
        """Return the byte-order-marker hook.

        Returns:
            `fix_byte_order_marker_hook`, wrapped in a single-element tuple.
        """
        return (self.fix_byte_order_marker_hook(),)

    def fix_byte_order_marker_hook(self) -> dict[str, Any]:
        """Return the hook metadata for stripping a leading byte-order mark.

        Runs first among the sequential text-fixing hooks, right after
        project synchronization: a leading BOM is a byte-level artifact
        that can confuse how every later hook reads the file as text (for
        example, hiding a shebang behind it), so it's removed before
        anything else touches file content.

        Returns:
            Hook metadata dict for `fix-byte-order-marker`.
        """
        return VersionControlHookManager.I.hook(
            self.fix_byte_order_marker,
            priority=VersionControlHookManager.I.increase_priority(
                Pyrigger.I.synchronize_project_hook(),
            ),
            types=["text"],
        )

    def fix_byte_order_marker(self) -> Args:
        """Return the `Args` this hook's entry runs.

        Returns:
            Args for `fix-byte-order-marker`.
        """
        return self.format_args()
