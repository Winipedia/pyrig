"""Abstract bases for `Tool` subclasses that contribute prek hooks."""

from abc import abstractmethod
from collections.abc import Iterable
from typing import Any

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Tool
from pyrig.rig.tools.version_control.hooks.manager import VersionControlHookManager


class VersionControlHookTool(Tool):
    """Abstract base for a `Tool` that contributes hooks to the prek pipeline.

    Replaces `Tool.version_control_hooks()` as the method a subclass
    overrides: `hooks()` is abstract here, so every concrete subclass must
    declare its hooks explicitly rather than silently inheriting the empty
    tuple `Tool.version_control_hooks()` falls back to.
    """

    @abstractmethod
    def hooks(self) -> tuple[dict[str, Any], ...]:
        """Return the prek hooks this tool contributes to the pipeline."""
        return ()

    @classmethod
    def subclasses_hooks(cls) -> Iterable[dict[str, Any]]:
        """Return every concrete tool's hooks, sorted for a deterministic pipeline.

        Returns:
            Every hook returned by `version_control_hooks()` across all
            concrete `Tool` subclasses, sorted via `sort_hooks`.
        """
        return (hook for tool in cls.concrete_subclasses() for hook in tool().hooks())

    @classmethod
    def sort_hooks(cls, hooks: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
        """Return the given hooks sorted for a deterministic pipeline.

        Sorts by the sort key returned by `hook_sort_key()`.

        Args:
            hooks: The hooks to sort.

        Returns:
            The hooks sorted by `(stages, priority, id)`.
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
        """Return `check_hook()`, wrapped in a single-element tuple.

        Returns:
            `check_hook()`, wrapped in a single-element tuple.
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
        """Return `format_hook()`, wrapped in a single-element tuple.

        Returns:
            `format_hook()`, wrapped in a single-element tuple.
        """
        return (*super().hooks(), self.format_hook())


class CheckFormatHookTool(CheckHookTool, FormatHookTool):
    """Abstract base for a `Tool` that has both a check hook and a format hook.

    `hooks()` combines both via cooperative inheritance: `CheckHookTool` and
    `FormatHookTool` each append their own hook on top of `super().hooks()`,
    so a concrete subclass gets both hooks without overriding `hooks()`
    itself.
    """
