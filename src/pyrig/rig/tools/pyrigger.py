"""Wrapper around pyrig.

Provides a type-safe wrapper for pyrig commands and information.
"""

from collections.abc import Callable
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
    """Pyrig CLI wrapper and project initialization orchestrator.

    Constructs pyrig command arguments for programmatic execution and
    orchestrates the full setup sequence for new pyrig projects.

    Operations:
        - Command construction: Build ``Args`` for any pyrig subcommand
        - Project initialization: Orchestrate the full ordered setup sequence
    """

    def name(self) -> str:
        """Get tool name.

        Returns:
            'pyrig'
        """
        return snake_to_kebab_case(pyrig.__name__)

    def group(self) -> str:
        """Returns the group the tool belongs to.

        Returns:
            `Group.TOOLING`
        """
        return Group.TOOLING

    def image_url(self) -> str:
        """Return the badge image URL for pyrig.

        Returns:
            The URL of the badge image as a string.
        """
        return f"https://img.shields.io/badge/built%20with-{self.name()}-3776AB?logo=buildkite&logoColor=black"

    def link_url(self) -> str:
        """Return the link URL for pyrig.

        Returns:
            The URL of the GitHub repository page as a string.
        """
        return f"https://github.com/Winipedia/{self.name()}"

    def cmd_args(self, *args: str, cmd: Callable[..., Any]) -> Args:
        """Construct pyrig command arguments from a callable.

        Derives the CLI command name from the callable's ``__name__``
        attribute by converting it from snake_case to kebab-case
        (e.g., ``my_command`` → ``my-command``), then prepends
        ``"pyrig"`` to form a complete command.

        Args:
            *args: Additional arguments appended after the command name.
            cmd: Callable whose ``__name__`` is used as the command name.

        Returns:
            Args for ``'pyrig <cmd_name> [args...]'``.
        """
        cmd_name = snake_to_kebab_case(cmd.__name__)  # ty:ignore[unresolved-attribute]
        return self.args(cmd_name, *args)

    def group_cmd_args(self, *args: str, group: str, cmd: Callable[..., Any]) -> Args:
        """Construct pyrig command arguments for a subcommand within a command group.

        Resolves the group name by searching the subcommands module for the given
        ``typer.Typer`` instance by identity (the same strategy used by the CLI
        builder), then derives the command name from the callable's ``__name__``
        in kebab-case.

        Args:
            *args: Additional arguments appended after the command name.
            group: The ``typer.Typer`` group app (e.g. ``make.app``).
            cmd: Callable whose ``__name__`` is used as the subcommand name.

        Returns:
            Args for ``'pyrig <group_name> <cmd_name> [args...]'``.

        Raises:
            StopIteration: If ``group`` is not registered in the subcommands module.
        """
        group_name = snake_to_kebab_case(group)
        cmd_name = snake_to_kebab_case(cmd.__name__)  # ty:ignore[unresolved-attribute]
        return self.args(group_name, cmd_name, *args)

    def init_project(self) -> None:
        """Run the full project initialization sequence.

        Fetches all setup steps from ``setup_steps()``, then executes them
        in order. Each step's ``Args`` object is wrapped with
        ``PackageManager.I.run_args`` (i.e., ``uv run <args>``)
        to ensure commands run inside the project's virtual environment.
        The progress bar advances after each step completes.
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

        Each step is a ``(Args, RunKwargs)`` pair. ``Args`` holds the command
        to run; ``RunKwargs`` is passed directly to ``Args.run()`` and is empty
        for most steps. The sync step uses ``{"check": False}`` because it
        exits with code 1 whenever it creates or updates files — expected on a
        fresh project. The final git commit triggers the pre-commit hook, which
        re-runs sync and acts as the convergence gate.

        Returns:
            Ordered list of ``(Args, RunKwargs)`` steps.
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
        """Returns pyrigs runtime dependency."""
        return snake_to_kebab_case(pyrig_runtime.__name__)
