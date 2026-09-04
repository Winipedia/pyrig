"""Wrapper around the ShellCheck shell script linter tool."""

from typing import Any

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.hooks import CheckHookTool
from pyrig.rig.tools.base.tool import Group
from pyrig.rig.tools.packages.manager import PackageManager
from pyrig.rig.tools.typing.checker import TypeChecker
from pyrig.rig.tools.version_control.hooks.manager import VersionControlHookManager


class ShellLinter(CheckHookTool):
    """Type-safe wrapper for the ShellCheck shell script linter."""

    def group(self) -> str:
        """Return `Group.CODE_QUALITY`, the badge group this tool belongs to."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the badge image URL for ShellCheck."""
        return f"https://img.shields.io/badge/shell-{self.shield_name()}-blue"

    def link_url(self) -> str:
        """Return the URL of the ShellCheck project page."""
        return "https://github.com/koalaman/shellcheck"

    def name(self) -> str:
        """Return `'shellcheck'`, the executable name for this tool's CLI command."""
        return "shellcheck"

    def dev_dependencies(self) -> tuple[str, ...]:
        """Return `('shellcheck-py',)`, the PyPI package providing `shellcheck`."""
        return ("shellcheck-py",)

    def dialect(self) -> str:
        """Return `"bash"`, the shell dialect this project standardizes on.

        The single source of truth for the dialect.

        Returns:
            The shell dialect name.
        """
        return "bash"

    def check_args(self, *args: str) -> Args:
        """Construct ShellCheck check arguments.

        No severity, dialect, or rule configuration is baked in here; the
        hook's own `args=` supplies those flags, and callers are otherwise
        expected to supply the specific files to check.

        Args:
            *args: Additional arguments forwarded to `shellcheck`, typically
                the file paths to check.

        Returns:
            Args for `shellcheck`.
        """
        return self.args(*args)

    def check_hook(self) -> dict[str, Any]:
        """Return hook metadata for linting shell scripts.

        Returns:
            Hook metadata dict for `shellcheck --enable=all
            --check-sourced --external-sources --norc --shell=bash`.
        """
        return VersionControlHookManager.I.hook(
            self.lint_shell,
            priority=VersionControlHookManager.I.hook_priority(
                TypeChecker.I.check_hook(),
            ),
            types=["shell"],
            args=[
                "--check-sourced",
                "--enable=all",
                "--external-sources",
                "--norc",
                f"--shell={self.dialect()}",
            ],
        )

    def lint_shell(self) -> Args:
        """Return the `Args` this hook's entry runs.

        Returns:
            Args for `uv run shellcheck`.
        """
        return PackageManager.I.run_args(*self.check_args())
