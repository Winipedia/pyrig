"""Wrapper around pyrig.

Provides a type-safe wrapper for pyrig commands and information.
"""

from collections.abc import Callable
from typing import Any

from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
)

import pyrig
from pyrig.core.strings import (
    snake_to_kebab_case,
)
from pyrig.core.subprocesses import Args
from pyrig.rig.cli.subcommands import mkroot, mktests
from pyrig.rig.tools.base.tool import Tool, ToolGroup
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.project_tester import ProjectTester
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

    Example:
        >>> from pyrig.rig.cli.subcommands import build
        >>> Pyrigger.I.cmd_args(cmd=build).run()
        >>> Pyrigger.I.init_project()
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
            `ToolGroup.TOOLING`
        """
        return ToolGroup.TOOLING

    def badge_urls(self) -> tuple[str, str]:
        """Get pyrig badge image URL and GitHub page URL."""
        return (
            f"https://img.shields.io/badge/built%20with-{self.name()}-3776AB?logo=buildkite&logoColor=black",
            f"https://github.com/Winipedia/{self.name()}",
        )

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
        return ("pyrig-dev",)

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
        with Progress(
            TextColumn("[bold]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
        ) as progress:
            task = progress.add_task("Initializing project", total=len(steps))
            for step_name, step_args in steps.items():
                progress.update(task, description=step_name)
                PackageManager.I.run_args(*step_args).run()
                progress.advance(task)
            progress.update(task, description="[green]Initialization complete!")

    def setup_steps(self) -> dict[str, Args]:
        """Return the ordered setup steps for project initialization.

        Each step is represented as a key-value pair where the key is a
        human-readable description of the step, and the value is an
        ``Args`` object containing the command arguments to execute that step.

        Returns:
            Ordered dict of setup steps with descriptions and command arguments.
        """
        return {
            "Initializing version control": VersionController.I.init_args(),
            "Adding dev dependencies": PackageManager.I.add_dev_dependencies_args(
                *Tool.subclasses_dev_dependencies()
            ),
            "Installing dependencies": PackageManager.I.install_dependencies_args(),
            "Creating project root": self.cmd_args(cmd=mkroot),
            "Installing project": PackageManager.I.install_dependencies_args(),
            "Creating tests": self.cmd_args(cmd=mktests),
            "Installing all version control hooks": (
                VersionControlHookManager.I.install_args()
            ),
            "Staging files for initial commit": VersionController.I.add_all_args(),
            "Running tests": ProjectTester.I.test_args(),
            "Committing initial changes": VersionController.I.commit_with_message_args(
                msg=f"{self.name()}: Initial commit"
            ),
        }
