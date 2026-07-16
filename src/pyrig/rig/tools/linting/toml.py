"""Command-line wrapper for the TOML linter and formatter."""

from typing import Any

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Group, Tool
from pyrig.rig.tools.formatting.end_of_file import EndOfFileFormatter
from pyrig.rig.tools.typing.checker import TypeChecker
from pyrig.rig.tools.version_control.hooks.manager import VersionControlHookManager


class TOMLLinter(Tool):
    """`tombi` command wrapper for linting and formatting."""

    def group(self) -> str:
        """Return `Group.CODE_QUALITY`."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the badge image URL for tombi."""
        return f"https://img.shields.io/badge/TOML-{self.shield_name()}-blueviolet"

    def link_url(self) -> str:
        """Return the URL of the tombi project page."""
        return "https://github.com/tombi-toml/tombi"

    def name(self) -> str:
        """Return `"tombi"`."""
        return "tombi"

    def check_args(self, *args: str) -> Args:
        """Build a `tombi lint` command.

        Args:
            *args: Additional arguments appended to the command.

        Returns:
            Args for `tombi lint`.
        """
        return self.args("lint", *args)

    def format_args(self, *args: str) -> Args:
        """Build a `tombi format` command.

        Args:
            *args: Additional arguments appended to the command.

        Returns:
            Args for `tombi format`.
        """
        return self.args("format", *args)

    def version_control_hooks(self) -> tuple[dict[str, Any], ...]:
        """Return the TOML linting and formatting hooks.

        Returns:
            `lint_toml_hook` and `format_toml_hook`, in that order.
        """
        return (self.lint_toml_hook(), self.format_toml_hook())

    def lint_toml_hook(self) -> dict[str, Any]:
        """Return the hook metadata for linting TOML files.

        tombi's lint has no auto-fix mode, so unlike the other linters it
        never mutates a file; it belongs with the pure-validation checks
        tier rather than the file-type-specific fixers. Its diagnostics
        also default to warn-level, which alone would never fail the hook,
        so `--error-on-warnings` is passed to make any warning fail it.

        Ties its priority to `TypeChecker.check_types_hook` so it runs
        alongside the rest of the checks tier rather than after it.

        Returns:
            Hook metadata dict for `tombi lint --error-on-warnings`.
        """
        return VersionControlHookManager.I.hook(
            self.lint_toml,
            priority=VersionControlHookManager.I.hook_priority(
                TypeChecker.I.check_types_hook(),
            ),
            types=["toml"],
            args=["--error-on-warnings"],
        )

    def lint_toml(self) -> Args:
        """Return the `Args` this hook's entry runs.

        Returns:
            Args for `tombi lint`.
        """
        return self.check_args()

    def format_toml_hook(self) -> dict[str, Any]:
        """Return the hook metadata for formatting TOML files.

        tombi lint never mutates a file, so there's no fix for formatting
        to run after; this can sit with the other file-type-specific
        fixers instead of being chained after `lint_toml_hook`.

        Runs after the sequential text-fixing chain, alongside the other
        file-type-specific fixers.

        Returns:
            Hook metadata dict for `tombi format`.
        """
        return VersionControlHookManager.I.hook(
            self.format_toml,
            priority=VersionControlHookManager.I.increase_priority(
                EndOfFileFormatter.I.format_end_of_file_hook(),
            ),
            types=["toml"],
        )

    def format_toml(self) -> Args:
        """Return the `Args` this hook's entry runs.

        Returns:
            Args for `tombi format`.
        """
        return self.format_args()
