"""Vulnerability scanning for installed Python dependencies."""

from typing import Any

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.hooks import CheckHookTool
from pyrig.rig.tools.base.tool import Group
from pyrig.rig.tools.typing.checker import TypeChecker
from pyrig.rig.tools.version_control.hooks.manager import VersionControlHookManager


class DependencyAuditor(CheckHookTool):
    """`pip-audit` command wrapper.

    Intentionally minimal so that downstream projects can subclass and
    override `check_args` to apply project-specific flags such as custom
    ignore lists or output formats.
    """

    def group(self) -> str:
        """Return `Group.CODE_QUALITY`."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the Shields.io badge URL advertising `pip-audit`."""
        return f"https://img.shields.io/badge/security-{self.shield_name()}-blue?logo=python"

    def link_url(self) -> str:
        """Return the URL of the `pip-audit` project page."""
        return "https://github.com/pypa/pip-audit"

    def name(self) -> str:
        """Return `"pip-audit"`."""
        return "pip-audit"

    def check_args(self, *args: str) -> Args:
        """Build the `pip-audit` command.

        Args:
            *args: Additional CLI flags for `pip-audit`.

        Returns:
            Args for running `pip-audit` with the given flags.
        """
        return self.args(*args)

    def check_hook(self) -> dict[str, Any]:
        """Return the hook metadata for auditing installed dependencies.

        Runs on the transition stages rather than pre-commit, since
        `pip-audit` scans installed distributions, not changed files. Ties
        its priority to `TypeChecker.check_hook`: it's a read-only
        check like the rest of that tier, so a full `--group all` sweep can
        run it alongside them even though it triggers on different stages.

        Returns:
            Hook metadata dict for `pip-audit`.
        """
        return VersionControlHookManager.I.hook(
            self.audit_dependencies,
            priority=VersionControlHookManager.I.hook_priority(
                TypeChecker.I.check_hook(),
            ),
            stages=VersionControlHookManager.I.transition_stages(),
            pass_filenames=False,
            always_run=True,
        )

    def audit_dependencies(self) -> Args:
        """Return the `Args` this hook's entry runs.

        Returns:
            Args for `pip-audit`.
        """
        return self.check_args()
