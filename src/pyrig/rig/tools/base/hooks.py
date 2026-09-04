"""Abstract bases for CLI tool wrappers that contribute prek hooks."""

from abc import abstractmethod
from collections.abc import Iterable
from typing import Any

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Tool
from pyrig.rig.tools.version_control.hooks.manager import VersionControlHookManager


class VersionControlHookTool(Tool):
    """Abstract base for a `Tool` that contributes hooks to the prek pipeline.

    `hooks()` is abstract, so a concrete subclass must always declare which
    hooks it contributes instead of silently contributing none.
    """

    @abstractmethod
    def hooks(self) -> tuple[dict[str, Any], ...]:
        """Return the prek hooks this tool contributes to the pipeline.

        Defaults to an empty tuple. A subclass that mixes in another
        hook-contributing base should include `super().hooks()` in the
        result, so that base's hooks are combined with its own rather than
        dropped.

        Returns:
            This tool's hook metadata dictionaries.
        """
        return ()

    @classmethod
    def subclasses_hooks(cls) -> list[dict[str, Any]]:
        """Return every concrete tool's hooks, sorted for a deterministic pipeline.

        Returns:
            Every hook returned by `hooks()` across all concrete subclasses,
            sorted via `sorted_hooks()`.
        """
        return cls.sorted_hooks(
            hook for tool in cls.concrete_leaves() for hook in tool().hooks()
        )

    @classmethod
    def sorted_hooks(cls, hooks: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
        """Return the given hooks sorted for a deterministic pipeline.

        Args:
            hooks: The hooks to sort.

        Returns:
            The hooks sorted by `hook_sort_key()`.
        """
        return sorted(
            hooks,
            key=VersionControlHookManager.I.hook_sort_key,
        )


class CheckHookTool(VersionControlHookTool):
    """Abstract base for a `Tool` whose one hook lints or validates files.

    Covers both a pure report-only check and a check that autofixes via its
    own flag (e.g. `--fix`): either way, this is the tool's linting or
    validation pass, as opposed to a separate dedicated formatting pass (see
    `FormatHookTool`).
    """

    @abstractmethod
    def check_args(self, *args: str) -> Args:
        """Build the `Args` for running this tool's check."""

    @abstractmethod
    def check_hook(self) -> dict[str, Any]:
        """Return this tool's check hook metadata."""

    def hooks(self) -> tuple[dict[str, Any], ...]:
        """Return `super().hooks()` with this tool's check hook appended.

        Returns:
            `super().hooks()` with `check_hook()` appended.
        """
        return (*super().hooks(), self.check_hook())


class FormatHookTool(VersionControlHookTool):
    """Abstract base for a `Tool` whose one hook formats/mutates files."""

    @abstractmethod
    def format_args(self, *args: str) -> Args:
        """Build the `Args` for running this tool's formatter."""

    @abstractmethod
    def format_hook(self) -> dict[str, Any]:
        """Return this tool's format hook metadata."""

    def hooks(self) -> tuple[dict[str, Any], ...]:
        """Return `super().hooks()` with this tool's format hook appended.

        Returns:
            `super().hooks()` with `format_hook()` appended.
        """
        return (*super().hooks(), self.format_hook())


class CheckFormatHookTool(CheckHookTool, FormatHookTool):
    """Tool with both check and format hooks."""
