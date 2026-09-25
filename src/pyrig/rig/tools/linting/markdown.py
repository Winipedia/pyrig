"""Wrapper around the rumdl Markdown linter and formatter."""

from typing import Any

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.hooks import CheckFormatHookTool
from pyrig.rig.tools.base.tool import Group
from pyrig.rig.tools.linting.python import PythonLinter
from pyrig.rig.tools.packages.manager import PackageManager
from pyrig.rig.tools.security.secrets import SecretsChecker
from pyrig.rig.tools.version_control.hooks.manager import VersionControlHookManager


class MarkdownLinter(CheckFormatHookTool):
    """Type-safe wrapper for the rumdl markdown linter.

    Constructs rumdl command-line arguments for linting and, separately,
    formatting markdown files.
    """

    def group(self) -> str:
        """Return `Group.CODE_QUALITY`, the badge group this tool belongs to."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the badge image URL for rumdl."""
        return f"https://img.shields.io/badge/Markdown-{self.shield_name()}-darkgreen"

    def link_url(self) -> str:
        """Return the URL of the rumdl project page."""
        return "https://github.com/rvben/rumdl"

    def name(self) -> str:
        """Return `'rumdl'`, the executable name for this tool's CLI command."""
        return "rumdl"

    def version_control_ignore_patterns(self) -> tuple[str, ...]:
        """Return `('.rumdl_cache/',)`, rumdl's cache directory."""
        return (".rumdl_cache/",)

    def check_args(self, *args: str) -> Args:
        """Construct rumdl check arguments.

        Args:
            *args: Additional arguments forwarded to `rumdl check`.

        Returns:
            Args for `rumdl check`.
        """
        return self.args("check", *args)

    def format_args(self, *args: str) -> Args:
        """Construct rumdl fmt arguments.

        Args:
            *args: Additional arguments forwarded to `rumdl fmt`.

        Returns:
            Args for `rumdl fmt`.
        """
        return self.args("fmt", *args)

    def check_hook(self) -> dict[str, Any]:
        """Return the hook metadata for linting Markdown files.

        Runs after Markdown formatting so it checks the final Markdown
        contents.

        Returns:
            Hook metadata dict for `rumdl check --deny-config-warnings`.
        """
        return VersionControlHookManager.I.local_hook(
            self.lint_markdown,
            priority=VersionControlHookManager.I.deprioritize(
                self.format_hook(),
                PythonLinter.I.format_hook(),
            ),
            types=["markdown"],
            args=self.hook_args(),
        )

    def lint_markdown(self) -> Args:
        """Return the `Args` this hook's entry runs.

        Returns:
            Args for `uv run rumdl check`.
        """
        return PackageManager.I.run_args(*self.check_args())

    def format_hook(self) -> dict[str, Any]:
        """Return the hook metadata for formatting Markdown files.

        Runs after the general read-only checks and before Ruff formats
        Python blocks in Markdown.

        Returns:
            Hook metadata dict for `rumdl fmt --deny-config-warnings`.
        """
        return VersionControlHookManager.I.local_hook(
            self.format_markdown,
            priority=VersionControlHookManager.I.deprioritize(
                SecretsChecker.I.check_hook(),
            ),
            types=["markdown"],
            args=self.hook_args(),
        )

    def format_markdown(self) -> Args:
        """Return the `Args` this hook's entry runs.

        Returns:
            Args for `uv run rumdl fmt`.
        """
        return PackageManager.I.run_args(*self.format_args())

    def hook_args(self, *args: str) -> Args:
        """Construct generic hook arguments both hooks use.

        Args:
            *args: Additional arguments forwarded to the hook.

        Returns:
            Args for the hook.
        """
        return Args("--deny-config-warnings", *args)
