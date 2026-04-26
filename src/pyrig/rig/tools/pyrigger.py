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
    make_name_from_obj,
    snake_to_kebab_case,
)
from pyrig.core.subprocesses import Args
from pyrig.rig.cli.subcommands import mkroot, mktests
from pyrig.rig.tools.base.tool import Tool, ToolGroup
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.pre_committer import (
    PreCommitter,
)
from pyrig.rig.tools.project_tester import ProjectTester
from pyrig.rig.tools.version_controller import VersionController


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
        in order. Each step method returns an ``Args`` object which is
        wrapped with ``PackageManager.I.run_args`` (i.e., ``uv run <args>``)
        to ensure commands run inside the project's virtual environment.
        The progress bar description is updated to the step method's human-
        readable name before each step runs, and advances after it completes.
        The process stops immediately if any step exits with a non-zero
        return code.

        Note:
            Intended to be run once during initial project setup, not as
            part of routine development.
        """
        steps = self.setup_steps()
        total = len(steps)
        with Progress(
            TextColumn("[bold]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
        ) as progress:
            task = progress.add_task("Initializing project", total=total)
            for step in steps:
                step_name = make_name_from_obj(step, join_on=" ")
                progress.update(task, description=step_name)
                PackageManager.I.run_args(*step()).run()
                progress.advance(task)
            progress.update(task, description="[green]Initialization complete!")

    def setup_steps(self) -> tuple[Callable[..., Args], ...]:
        """Return the ordered tuple of project setup step methods.

        Each method takes no arguments and returns an ``Args`` object.
        Steps are executed in the listed order by ``init_project()``.

        ``installing_dependencies`` appears twice: first to install dev
        dependencies after they are added to ``pyproject.toml``, and
        again after ``creating_project_root`` updates ``pyproject.toml``
        with the generated project configuration.

        Returns:
            Ordered tuple of callables, each returning an ``Args`` object.
        """
        return (
            self.initializing_version_control,
            self.adding_dev_dependencies,
            # to install dev deps
            self.installing_dependencies,
            self.creating_project_root,
            # to install project bc of pyproject.toml changes
            self.installing_dependencies,
            self.creating_test_files,
            self.install_pre_commit_hooks,
            self.add_all_files_to_version_control,
            self.running_pre_commit_hooks,
            self.running_tests,
            self.committing_initial_changes,
        )

    def initializing_version_control(self) -> Args:
        """Return args for initializing a git repository via `git init`."""
        return VersionController.I.init_args()

    def adding_dev_dependencies(self) -> Args:
        """Return args for adding dev dependencies via `uv add --group dev`.

        Returns:
            `Args` for adding pyrig's standard dev dependencies to
            `pyproject.toml`.
        """
        return PackageManager.I.add_dev_dependencies_args(
            *Tool.subclasses_dev_dependencies()
        )

    def installing_dependencies(self) -> Args:
        """Return args for installing the virtual environment via `uv sync`.

        Installs all dependencies from `pyproject.toml`. Called twice during
        initialization: after adding dev dependencies and after creating the
        project root.
        """
        return PackageManager.I.install_dependencies_args()

    def creating_project_root(self) -> Args:
        """Return args for creating project structure and config files.

        Generates all remaining configuration files and directory structure
        via `pyrig mkroot`.
        """
        return self.cmd_args(cmd=mkroot)

    def creating_test_files(self) -> Args:
        """Return args for generating test skeletons via `pyrig mktests`.

        Creates test files mirroring the source package structure with
        `NotImplementedError` placeholders.
        """
        return self.cmd_args(cmd=mktests)

    def install_pre_commit_hooks(self) -> Args:
        """Return args for installing prek hooks via `prek install`."""
        return PreCommitter.I.install_args()

    def add_all_files_to_version_control(self) -> Args:
        """Return args for staging all files via `git add .`."""
        return VersionController.I.add_all_args()

    def running_pre_commit_hooks(self) -> Args:
        """Return args for running prek hooks via `prek run --all-files`.

        Runs formatters and linters on all files to ensure the codebase follows
        style guidelines.
        """
        return PreCommitter.I.run_all_files_args()

    def running_tests(self) -> Args:
        """Return args for running the test suite via `pytest`.

        Validates that all generated code is syntactically correct and the project
        is properly configured.
        """
        return ProjectTester.I.test_args()

    def committing_initial_changes(self) -> Args:
        """Return args for creating the initial git commit.

        Commits all configuration files, test skeletons, and formatting
        changes with the message ``"pyrig: Initial commit"``. Uses
        ``--no-verify`` to skip re-running pre-commit hooks, since they
        were already executed in the preceding ``running_pre_commit_hooks``
        step and all staged changes are already clean.
        """
        # changes were added by the run prek hooks step
        return VersionController.I.commit_no_verify_args(
            msg=f"{self.name()}: Initial commit"
        )
