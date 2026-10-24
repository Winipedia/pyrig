"""Command-line wrapper for Python source ordering."""

from typing import Any

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.hooks import CheckHookTool
from pyrig.rig.tools.base.tool import Group
from pyrig.rig.tools.packages.manager import PackageManager
from pyrig.rig.tools.security.secrets import SecretsChecker
from pyrig.rig.tools.version_control.hooks.manager import VersionControlHookManager


class PythonOrderLinter(CheckHookTool):
    """`pyorder` command wrapper for checking and fixing definition order."""

    def group(self) -> str:
        """Return `Group.CODE_QUALITY`."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the badge image URL for pyorder."""
        return "https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/Winipedia/pyorder/main/docs/assets/badge.json"

    def link_url(self) -> str:
        """Return the URL of the pyorder project page."""
        return "https://github.com/Winipedia/pyorder"

    def name(self) -> str:
        """Return `"pyorder"`."""
        return "pyorder"

    def check_args(self, *args: str) -> Args:
        """Build a `pyorder check` command.

        Args:
            *args: Additional arguments appended to the command.

        Returns:
            Args for `pyorder check`.
        """
        return self.args("check", *args)

    def check_hook(self) -> dict[str, Any]:
        """Return hook metadata for fixing Python definition order.

        Runs after the secrets check and before Ruff's autofixing linter.

        Returns:
            Hook metadata dict for `pyorder check --fix`.
        """
        return VersionControlHookManager.I.local_hook(
            self.lint_python_order,
            priority=VersionControlHookManager.I.deprioritize(
                SecretsChecker.I.check_hook(),
            ),
            types=["python"],
            args=Args("--fix"),
        )

    def lint_python_order(self) -> Args:
        """Return the `Args` this hook's entry runs.

        Returns:
            Args for `uv run pyorder check`.
        """
        return PackageManager.I.run_args(*self.check_args())
