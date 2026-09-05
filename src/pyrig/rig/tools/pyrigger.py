"""Tool wrapper for the pyrig CLI itself, including new-project initialization."""

from types import FunctionType
from typing import Any

import pyrig_runtime
import typer
from pyrig_runtime.core.strings import snake_to_kebab_case

import pyrig
from pyrig.core.subprocesses import Args
from pyrig.rig.cli.subcommands import sync
from pyrig.rig.configs.base.config_file import ConfigFile
from pyrig.rig.tools.base.hooks import VersionControlHookTool
from pyrig.rig.tools.base.tool import Group
from pyrig.rig.tools.packages.manager import PackageManager
from pyrig.rig.tools.version_control.controller import VersionController
from pyrig.rig.tools.version_control.hooks.manager import (
    VersionControlHookManager,
)


class Pyrigger(VersionControlHookTool):
    """Pyrig CLI wrapper and new-project initialization orchestrator."""

    def group(self) -> str:
        """Return `Group.TOOLING`."""
        return Group.TOOLING

    def image_url(self) -> str:
        """Return the badge image URL for pyrig."""
        return f"https://img.shields.io/badge/built%20with-{self.shield_name()}-3776AB?logo=buildkite&logoColor=black"

    def link_url(self) -> str:
        """Return the badge link URL for pyrig."""
        return f"https://github.com/Winipedia/{self.name()}"

    def name(self) -> str:
        """Return `"pyrig"`."""
        return snake_to_kebab_case(pyrig.__name__)

    def init_project(self) -> None:
        """Run the ordered project initialization sequence with a progress bar.

        Each step can independently choose to tolerate a non-zero return
        code; otherwise the process stops immediately at the failing step.

        Raises:
            RuntimeError: If the repository already has at least one commit.

        Note:
            Intended to be run once during initial project setup, not as
            part of routine development.

        Warning:
            Deletes every removable config file already present in the
            working directory before running the setup steps.
        """
        if VersionController.I.has_commits():
            msg = "cannot initialize project that already has commits"
            raise RuntimeError(msg)

        self.remove_config_files()

        steps = self.setup_steps()
        with typer.progressbar(
            steps,
            label="Initializing project",
            length=len(steps),
        ) as progress:
            for step_args, run_kwargs in progress:
                PackageManager.I.run_args(*step_args).run(**run_kwargs)

    def remove_config_files(self) -> None:
        """Delete every removable config file that currently exists.

        Config files whose `removable()` returns `False`, such as
        `pyproject.toml`, are left untouched.
        """
        for config_file in (cf().path() for cf in ConfigFile.removable_subclasses()):
            if config_file.exists():
                config_file.unlink()

    def setup_steps(self) -> tuple[tuple[Args, dict[str, Any]], ...]:
        """Return the ordered setup steps for project initialization.

        Each step pairs the command to run with the keyword arguments to pass
        to its `.run()` call. The sync step tolerates a non-zero exit, since
        syncing a fresh project is expected to create or update files.

        Returns:
            Ordered list of `(Args, run_kwargs)` steps.
        """
        return (
            (VersionController.I.init_args(), {}),
            (self.cmd_args(cmd=sync), {"check": False}),
            (VersionController.I.add_all_args(), {}),
            (VersionController.I.commit_with_msg_args(msg=self.setup_commit_msg()), {}),
        )

    def setup_commit_msg(self) -> str:
        """Return the commit message for the initial commit."""
        return f"{self.name()}: Initialized project"

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
        return self.args(snake_to_kebab_case(cmd.__name__), *args)

    def runtime_dependencies(self) -> list[str]:
        """Return the runtime dependencies the target project must declare.

        Returns:
            List of runtime dependencies, including `"pyrig-runtime"`.
        """
        return [self.runtime_dependency()]

    def runtime_dependency(self) -> str:
        """Return `"pyrig-runtime"`, the package name of pyrig's runtime dependency."""
        return snake_to_kebab_case(pyrig_runtime.__name__)

    def hooks(self) -> tuple[dict[str, Any], ...]:
        """Return the project-synchronization hook.

        Returns:
            `synchronize_project_hook`, wrapped in a single-element tuple.
        """
        return (self.synchronize_project_hook(),)

    def synchronize_project_hook(self) -> dict[str, Any]:
        """Return the hook metadata for the `pyrig sync` hook."""
        return VersionControlHookManager.I.hook(
            self.synchronize_project,
            priority=VersionControlHookManager.I.increase_priority(
                PackageManager.I.audit_dependencies_hook(),
            ),
        )

    def synchronize_project(self) -> Args:
        """Return the `Args` this hook's entry runs.

        Returns:
            Args for `uv run pyrig sync`.
        """
        return PackageManager.I.run_args(*self.cmd_args(cmd=sync))
