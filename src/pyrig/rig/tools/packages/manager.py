"""Wrapper for the project's package manager and source of its layout conventions."""

from pathlib import Path
from typing import Any

from pyrig_runtime.core.strings import kebab_to_snake_case, snake_to_kebab_case

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.hooks import VersionControlHookTool
from pyrig.rig.tools.base.tool import Group
from pyrig.rig.tools.version_control.hooks.manager import VersionControlHookManager


class PackageManager(VersionControlHookTool):
    """`uv` package manager wrapper and source of the project's layout conventions.

    Beyond the `*_args` methods that build commands for `uv`, this also exposes
    the project's name, package name, source layout, and build system
    configuration, since those follow conventions the package manager defines.

    Subclass and override `build_system_requires` and `build_backend` to use a
    different build back-end, `source_root` for a different project layout, and
    `dev_dependencies` if the package manager itself must be installed as a
    project dependency rather than assumed already present on the system.
    """

    def dev_dependencies(self) -> tuple[str, ...]:
        """Return an empty tuple: uv is a system-level tool, not a dev dependency."""
        return ()

    def group(self) -> str:
        """Return `Group.TOOLING`."""
        return Group.TOOLING

    def image_url(self) -> str:
        """Return the uv badge image URL."""
        return "https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json"

    def link_url(self) -> str:
        """Return the URL of the uv project page."""
        return "https://github.com/astral-sh/uv"

    def name(self) -> str:
        """Return `'uv'`."""
        return "uv"

    def version_control_ignore_patterns(self) -> tuple[str, ...]:
        """Return `(".venv", "dist/")`."""
        return (".venv", f"{self.dist_dir().as_posix()}/")

    def package_root(self) -> Path:
        """Return the directory where the importable package lives.

        Relative to the project root, e.g. `src/my_project`.
        """
        return self.source_root() / self.package_name()

    def package_name(self) -> str:
        """Return the importable Python package name.

        Given a project named `my-project`, returns `my_project`.
        """
        return kebab_to_snake_case(self.project_name())

    def project_name(self) -> str:
        """Return the project name, taken from the current working directory's name.

        By convention this matches the `[project] name` field in
        `pyproject.toml`.
        """
        return Path.cwd().name

    def source_root(self) -> Path:
        """Return `Path("src")`."""
        return Path("src")

    def build_backend(self) -> str:
        """Return `"uv_build"` for the `[build-system].build-backend` field.

        Override this alongside `build_system_requires` if the project uses a
        different build back-end.
        """
        return "uv_build"

    def build_system_requires(self) -> list[str]:
        """Return `["uv-build"]` for the `[build-system].requires` field.

        Override this alongside `build_backend` if the project uses a
        different build back-end, for example `["poetry-core"]` for Poetry or
        `["hatchling"]` for Hatch.
        """
        return [snake_to_kebab_case(self.build_backend())]

    def lock_file(self) -> Path:
        """Return `Path("uv.lock")`, relative to the project root."""
        return Path("uv.lock")

    def no_auto_install_env_var(self) -> str:
        """Return the name of the env var that disables uv's implicit auto-sync."""
        return "UV_NO_SYNC"

    def dist_dir(self) -> Path:
        """Return the relative directory where distribution artifacts are stored."""
        return Path("dist")

    def run_args(self, *args: str) -> Args:
        """Construct `Args` for `uv run`.

        Args:
            *args: Command and arguments to run.

        Returns:
            Args for `uv run <args...>`.
        """
        return self.args("run", *args)

    def add_group_dev_args(self, *args: str) -> Args:
        """Construct `Args` for adding packages to the dev dependency group.

        Args:
            *args: Package names or additional `uv add` flags.

        Returns:
            Args for `uv add --group=dev <args...>`.
        """
        return self.add_group_args(*args, group="dev")

    def add_group_args(self, *args: str, group: str) -> Args:
        """Construct `Args` for adding packages to a dependency group.

        Args:
            *args: Package names or additional `uv add` flags.
            group: The dependency group to add to.

        Returns:
            Args for `uv add --group=<group> <args...>`.
        """
        return self.add_args(f"--group={group}", *args)

    def add_args(self, *args: str) -> Args:
        """Construct `Args` for `uv add`.

        Args:
            *args: Package names or additional `uv add` flags.

        Returns:
            Args for `uv add <args...>`.
        """
        return self.args("add", *args)

    def remove_group_dev_args(self, *args: str) -> Args:
        """Construct `Args` for removing packages from the dev dependency group.

        Args:
            *args: Package names or additional `uv remove` flags.

        Returns:
            Args for `uv remove --group=dev <args...>`.
        """
        return self.remove_group_args(*args, group="dev")

    def remove_group_args(self, *args: str, group: str) -> Args:
        """Construct `Args` for removing packages from a dependency group.

        Args:
            *args: Package names or additional `uv remove` flags.
            group: The dependency group to remove from.

        Returns:
            Args for `uv remove --group=<group> <args...>`.
        """
        return self.remove_args(f"--group={group}", *args)

    def remove_args(self, *args: str) -> Args:
        """Construct `Args` for `uv remove`.

        Args:
            *args: Package names or additional `uv remove` flags.

        Returns:
            Args for `uv remove <args...>`.
        """
        return self.args("remove", *args)

    def audit_args(self, *args: str) -> Args:
        """Construct `Args` for `uv audit`.

        Args:
            *args: Additional arguments for the audit command.

        Returns:
            Args for `uv audit <args...>`.
        """
        return self.args("audit", *args)

    def install_dependencies_no_dev_args(self, *args: str) -> Args:
        """Construct `Args` for `uv sync --no-group=dev`.

        Args:
            *args: Additional arguments for the sync command.

        Returns:
            Args for `uv sync --no-group=dev <args...>`.
        """
        return self.install_dependencies_no_group_args(*args, group="dev")

    def install_dependencies_no_group_args(self, *args: str, group: str) -> Args:
        """Construct `Args` for `uv sync --no-group=<group>`.

        Args:
            *args: Additional arguments for the sync command.
            group: The dependency group to exclude from installation.

        Returns:
            Args for `uv sync --no-group=<group> <args...>`.
        """
        return self.install_dependencies_args(f"--no-group={group}", *args)

    def install_dependencies_args(self, *args: str) -> Args:
        """Construct `Args` for `uv sync`.

        Synchronizes the environment to match the lock file exactly,
        installing and removing packages as needed.

        Args:
            *args: Additional arguments for the sync command.

        Returns:
            Args for `uv sync <args...>`.
        """
        return self.args("sync", *args)

    def update_dependencies_args(self, *args: str) -> Args:
        """Construct `Args` for upgrading all locked dependency versions.

        Updates the lock file only; it does not install anything.

        Args:
            *args: Additional arguments for the lock command.

        Returns:
            Args for `uv lock --upgrade <args...>`.
        """
        return self.args("lock", "--upgrade", *args)

    def version_short_args(self, *args: str) -> Args:
        """Construct `Args` for reading the current project version as a bare string.

        Args:
            *args: Additional arguments for the version command.

        Returns:
            Args for `uv version --short <args...>`.
        """
        return self.version_args("--short", *args)

    def version_args(self, *args: str) -> Args:
        """Construct `Args` for `uv version`.

        Args:
            *args: Additional arguments for the version command.

        Returns:
            Args for `uv version <args...>`.
        """
        return self.args("version", *args)

    def build_args(self, *args: str) -> Args:
        """Construct `Args` for `uv build`.

        Args:
            *args: Additional arguments for the build command.

        Returns:
            Args for `uv build <args...>`.
        """
        return self.args("build", *args)

    def hooks(self) -> tuple[dict[str, Any], ...]:
        """Return the dependency update, install, and audit hooks."""
        return (
            self.update_dependencies_hook(),
            self.install_dependencies_hook(),
            self.audit_dependencies_hook(),
        )

    def update_dependencies_hook(self) -> dict[str, Any]:
        """Return the hook metadata for upgrading locked dependency versions.

        Runs first among the transition-stage hooks, since every other step
        that touches dependencies depends on the lock file already being
        current.

        Returns:
            Hook metadata dict for `uv lock --upgrade`.
        """
        return VersionControlHookManager.I.hook(
            self.update_dependencies,
            priority=0,
            stages=VersionControlHookManager.I.transition_stages(),
            pass_filenames=False,
            always_run=True,
        )

    def update_dependencies(self) -> Args:
        """Return the `Args` this hook's entry runs.

        Returns:
            Args for `uv lock --upgrade`.
        """
        return self.update_dependencies_args()

    def install_dependencies_hook(self) -> dict[str, Any]:
        """Return the hook metadata for installing dependencies.

        Runs after `update_dependencies_hook`, since installing requires the
        lock file it refreshes.

        Returns:
            Hook metadata dict for `uv sync`.
        """
        return VersionControlHookManager.I.hook(
            self.install_dependencies,
            priority=VersionControlHookManager.I.increase_priority(
                self.update_dependencies_hook(),
            ),
            stages=VersionControlHookManager.I.transition_stages(),
            pass_filenames=False,
            always_run=True,
        )

    def install_dependencies(self) -> Args:
        """Return the `Args` this hook's entry runs.

        Returns:
            Args for `uv sync`.
        """
        return self.install_dependencies_args()

    def audit_dependencies_hook(self) -> dict[str, Any]:
        """Return the hook metadata for auditing installed dependencies.

        Runs after `install_dependencies_hook`, since auditing requires the
        dependencies it installs to already be present.

        Returns:
            Hook metadata dict for `uv audit`.
        """
        return VersionControlHookManager.I.hook(
            self.audit_dependencies,
            priority=VersionControlHookManager.I.increase_priority(
                self.install_dependencies_hook(),
            ),
            stages=VersionControlHookManager.I.transition_stages(),
            pass_filenames=False,
            always_run=True,
        )

    def audit_dependencies(self) -> Args:
        """Return the `Args` this hook's entry runs.

        Returns:
            Args for `uv audit`.
        """
        return self.audit_args()
