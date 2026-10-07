"""Dead code checker command construction and badge metadata."""

from typing import Any

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.hooks import CheckHookTool
from pyrig.rig.tools.base.tool import Group
from pyrig.rig.tools.linting.python import PythonLinter
from pyrig.rig.tools.packages.manager import PackageManager
from pyrig.rig.tools.version_control.hooks.manager import VersionControlHookManager


class DeadCodeChecker(CheckHookTool):
    """Wrapper for the `vulture` dead code checker."""

    def group(self) -> str:
        """Return `Group.CODE_QUALITY`."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the Shields.io badge URL advertising `vulture`."""
        return f"https://img.shields.io/badge/dead_code-{self.shield_name()}-blue"

    def link_url(self) -> str:
        """Return the URL of the `vulture` project page."""
        return "https://github.com/jendrikseipp/vulture"

    def name(self) -> str:
        """Return `"vulture"`."""
        return "vulture"

    def check_args(self, *args: str) -> Args:
        """Build the `vulture` command.

        Args:
            *args: Additional arguments appended to the command.

        Returns:
            Args for running `vulture` with the given arguments.
        """
        return self.args(*args)

    def check_hook(self) -> dict[str, Any]:
        """Return hook metadata for checking dead code.

        Returns:
            Hook metadata dict for `vulture`.
        """
        return VersionControlHookManager.I.local_hook(
            self.check_dead_code,
            priority=VersionControlHookManager.I.deprioritize(
                PythonLinter.I.format_hook(),
            ),
            types=["python"],
            pass_filenames=False,
        )

    def check_dead_code(self) -> Args:
        """Return the `Args` this hook's entry runs.

        Returns:
            Args for `uv run vulture`.
        """
        return PackageManager.I.run_args(*self.check_args())
