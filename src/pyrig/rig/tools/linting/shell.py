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

    def check_args(self, *args: str) -> Args:
        """Construct ShellCheck check arguments at maximum strictness.

        Enables every optional check on top of the default set, surfaces
        every severity level down to style, and pins the dialect to `bash`
        rather than relying on shebang detection, since every script this
        project generates (`ShellConfigFile`) commits to `bash` explicitly.

        Args:
            *args: Additional arguments forwarded to `shellcheck`, typically
                the file paths to check.

        Returns:
            Args for `shellcheck --severity=style --enable=all --shell=bash`.
        """
        return self.args(*args)

    def check_hook(self) -> dict[str, Any]:
        """Return the hook metadata for linting shell scripts.

        Ties its priority to `TypeChecker.check_hook` so it runs
        alongside the rest of the checks tier rather than after it.

        Returns:
            Hook metadata dict for `shellcheck`.
        """
        return VersionControlHookManager.I.hook(
            self.lint_shell,
            priority=VersionControlHookManager.I.hook_priority(
                TypeChecker.I.check_hook(),
            ),
            types=["shell"],
            args=[
                "--enable=all",
                "--severity=style",
                "--shell=bash",
            ],
        )

    def lint_shell(self) -> Args:
        """Return the `Args` this hook's entry runs.

        Returns:
            Args for `uv run shellcheck`.
        """
        return PackageManager.I.run_args(*self.check_args())
