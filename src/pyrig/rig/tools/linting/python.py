"""Command-line wrapper for the Python linter and formatter."""

from typing import Any

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Group, Tool
from pyrig.rig.tools.formatting.end_of_file import EndOfFileFormatter
from pyrig.rig.tools.version_control.hooks.manager import VersionControlHookManager


class PythonLinter(Tool):
    """`ruff` command wrapper for linting, auto-fixing, and formatting."""

    def group(self) -> str:
        """Return `Group.CODE_QUALITY`."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the Shields.io badge URL advertising `ruff`."""
        return "https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json"

    def link_url(self) -> str:
        """Return the URL of the `ruff` project page."""
        return "https://github.com/astral-sh/ruff"

    def name(self) -> str:
        """Return `"ruff"`."""
        return "ruff"

    def version_control_ignore_patterns(self) -> tuple[str, ...]:
        """Return `ruff`'s cache directory as the only path to ignore."""
        return (".ruff_cache/",)

    def lint_args(self, *args: str) -> Args:
        """Build a `ruff check` command.

        Args:
            *args: Additional arguments appended to the command.

        Returns:
            Args for `ruff check`.
        """
        return self.args("check", *args)

    def format_args(self, *args: str) -> Args:
        """Build a `ruff format` command.

        Args:
            *args: Additional arguments appended to the command.

        Returns:
            Args for `ruff format`.
        """
        return self.args("format", *args)

    def pydocstyle(self) -> str:
        """Return `google` as the docstring standard."""
        return "google"

    def version_control_hooks(self) -> tuple[dict[str, Any], ...]:
        """Return the Python linting and formatting hooks.

        Returns:
            `lint_hook` and `format_hook`, in that order.
        """
        return (self.lint_hook(), self.format_hook())

    def lint_hook(self) -> dict[str, Any]:
        """Return the hook metadata for linting and auto-fixing Python source.

        Runs after the sequential text-fixing chain, alongside the other
        file-type-specific fixers.

        Returns:
            Hook metadata dict for `ruff check --fix`.
        """
        return VersionControlHookManager.I.hook(
            self.lint_python,
            priority=VersionControlHookManager.I.increase_priority(
                EndOfFileFormatter.I.format_hook(),
            ),
            types=["python"],
            args=["--fix"],
        )

    def lint_python(self) -> Args:
        """Return the `Args` this hook's entry runs.

        Returns:
            Args for `ruff check`.
        """
        return self.lint_args()

    def format_hook(self) -> dict[str, Any]:
        """Return the hook metadata for formatting Python source.

        Runs after linting, so formatting never fights the fixes ruff's
        linter just applied.

        Returns:
            Hook metadata dict for `ruff format`.
        """
        return VersionControlHookManager.I.hook(
            self.format_python,
            priority=VersionControlHookManager.I.increase_priority(
                self.lint_hook(),
            ),
            types=["python"],
        )

    def format_python(self) -> Args:
        """Return the `Args` this hook's entry runs.

        Returns:
            Args for `ruff format`.
        """
        return self.format_args()
