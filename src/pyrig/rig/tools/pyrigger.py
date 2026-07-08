"""Tool wrapper for the pyrig CLI itself, used for self-referential commands."""

from types import FunctionType
from typing import Any

import pyrig_runtime
import typer
from pyrig_runtime.core.strings import snake_to_kebab_case

import pyrig
from pyrig.core.subprocesses import Args
from pyrig.rig.cli.subcommands import sync
from pyrig.rig.tools.base.tool import Group, Tool
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.version_control.hook_manager import (
    VersionControlHookManager,
)
from pyrig.rig.tools.version_control.version_controller import VersionController


class Pyrigger(Tool):
    """Pyrig CLI wrapper and new-project initialization orchestrator."""

    def group(self) -> str:
        """Return the badge group this tool belongs to.

        Returns:
            `Group.TOOLING`.
        """
        return Group.TOOLING

    def image_url(self) -> str:
        """Return the badge image URL for pyrig."""
        return f"https://img.shields.io/badge/built%20with-{self.name()}-3776AB?logo=buildkite&logoColor=black"

    def link_url(self) -> str:
        """Return the badge link URL for pyrig."""
        return f"https://github.com/Winipedia/{self.name()}"

    def name(self) -> str:
        """Return the pyrig executable name.

        Returns:
            `'pyrig'`.
        """
        return snake_to_kebab_case(pyrig.__name__)

    def cmd_args(self, *args: str, cmd: FunctionType) -> Args:
        """Construct `Args` for a top-level pyrig CLI command.

        Derives the command name from `cmd.__name__`, converted from
        snake_case to kebab-case (e.g. `my_command` becomes `my-command`).

        Args:
            *args: Additional arguments appended after the command name.
            cmd: Callable whose `__name__` is used as the command name.

        Returns:
            Args for `pyrig <cmd_name> [args...]`.
        """
        cmd_name = snake_to_kebab_case(cmd.__name__)
        return self.args(cmd_name, *args)

    def group_cmd_args(self, *args: str, group: str, cmd: FunctionType) -> Args:
        """Construct `Args` for a pyrig CLI subcommand within a command group.

        Converts both `group` and `cmd.__name__` from snake_case to
        kebab-case to derive the group and subcommand names.

        Args:
            *args: Additional arguments appended after the command name.
            group: Name of the command group, in snake_case.
            cmd: Callable whose `__name__` is used as the subcommand name.

        Returns:
            Args for `pyrig <group_name> <cmd_name> [args...]`.
        """
        group_name = snake_to_kebab_case(group)
        cmd_name = snake_to_kebab_case(cmd.__name__)
        return self.args(group_name, cmd_name, *args)

    def init_project(self) -> None:
        """Run the ordered project initialization sequence with a progress bar.

        The process stops immediately if any step exits with a non-zero
        return code.

        Note:
            Intended to be run once during initial project setup, not as
            part of routine development.
        """
        steps = self.setup_steps()
        with typer.progressbar(
            steps,
            label="Initializing project",
            length=len(steps),
        ) as progress:
            for step_args, run_kwargs in progress:
                PackageManager.I.run_args(*step_args).run(**run_kwargs)

    def setup_steps(self) -> list[tuple[Args, dict[str, Any]]]:
        """Return the ordered setup steps for project initialization.

        Each step pairs the command to run with the keyword arguments to pass
        to its `.run()` call. The sync step tolerates a non-zero exit, since
        syncing a fresh project is expected to create or update files.

        Returns:
            Ordered list of `(Args, run_kwargs)` steps.
        """
        return [
            (VersionController.I.init_args(), {}),
            (PackageManager.I.add_args(self.runtime_dependency()), {}),
            (
                PackageManager.I.add_dev_dependencies_args(
                    *Tool.subclasses_dev_dependencies()
                ),
                {},
            ),
            (PackageManager.I.install_dependencies_args(), {}),
            (self.cmd_args(cmd=sync), {"check": False}),
            (PackageManager.I.install_dependencies_args(), {}),
            (VersionControlHookManager.I.install_args(), {}),
            (VersionController.I.add_all_args(), {}),
            (
                VersionController.I.commit_with_msg_args(
                    msg=f"{self.name()}: Initial commit"
                ),
                {},
            ),
        ]

    def runtime_dependency(self) -> str:
        """Return the package name of pyrig's runtime dependency.

        Returns:
            `'pyrig-runtime'`.
        """
        return snake_to_kebab_case(pyrig_runtime.__name__)
