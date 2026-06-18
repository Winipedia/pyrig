"""Wrapper around pyrig.

Provides a type-safe wrapper for pyrig commands and information.
"""

from collections.abc import Callable
from typing import Any

import typer

import pyrig
from pyrig.core.strings import (
    snake_to_kebab_case,
)
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

    def dev_dependencies(self) -> tuple[str, ...]:
        """Get the development package dependencies for pyrig.

        Returns ``("pyrig-dev",)`` rather than ``("pyrig",)`` because
        ``pyrig`` is already declared as a runtime dependency of generated
        projects. The ``pyrig-dev`` package provides additional tooling
        needed only during development.

        Returns:
            ``("pyrig-dev",)``
        """
        # only pyrig-dev not pyrig because pyrig is already installed as dependency
        return (self.dev_dep(),)

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

    def dev_dep_cmd_args(self, *args: str, cmd: Callable[..., Any]) -> Args:
        """Make command args with pyrig-dev."""
        cmd_name = snake_to_kebab_case(cmd.__name__)  # ty:ignore[unresolved-attribute]
        return self.dev_dep_args(cmd_name, *args)

    def dev_dep_args(self, *args: str) -> Args:
        """Make args with pyrig-dev."""
        return Args((self.dev_dep(), *args))

    def dev_dep(self) -> str:
        """Get the pyrig-dev dev dependency."""
        return "pyrig-dev"

    def init_project(self) -> None:
        """Run the full project initialization sequence.

        Fetches all setup steps from ``setup_steps()``, then executes them
        in order. Each step's ``Args`` object is wrapped with
        ``PackageManager.I.run_args`` (i.e., ``uv run <args>``)
        to ensure commands run inside the project's virtual environment.
        The progress bar description is updated to the step's description
        (the dict key) before each step runs, and advances after it completes.
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
            for step_args in progress:
                PackageManager.I.run_args(*step_args).run()

    def setup_steps(self) -> list[Args]:
        """Return the ordered setup steps for project initialization.

        Each step is represented as a key-value pair where the key is a
        human-readable description of the step, and the value is an
        ``Args`` object containing the command arguments to execute that step.

        Returns:
            Ordered dict of setup steps with descriptions and command arguments.
        """
        return [
            VersionController.I.init_args(),
            PackageManager.I.add_dev_dependencies_args(
                *Tool.subclasses_dev_dependencies()
            ),
            PackageManager.I.install_dependencies_args(),
            self.cmd_args(cmd=sync),
            PackageManager.I.install_dependencies_args(),
            VersionControlHookManager.I.install_args(),
            VersionController.I.add_all_args(),
            VersionController.I.commit_with_message_args(
                msg=f"{self.name()}: Initial commit"
            ),
        ]
