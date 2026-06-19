"""Package manager wrapper.

Wraps PackageManager commands and information.
"""

from collections.abc import Callable
from pathlib import Path
from typing import Any

from pyrig.core.strings import (
    snake_to_kebab_case,
)
from pyrig.core.subprocesses import Args
from pyrig.rig.cli.cli.cli import CLI
from pyrig.rig.tools.base.tool import Group, Tool


class PackageManager(Tool):
    """uv package manager wrapper.

    The ``*_args()`` methods each construct a type-safe ``Args`` object for a
    specific uv command. Call ``.run()`` on the result to execute it, or
    convert it to a string to embed in CI workflow scripts.

    Subclass and override ``build_system_requires``, ``build_backend``,
    ``source_root``, or ``dev_dependencies`` to adapt pyrig to a different
    build back-end or project layout.
    """

    def name(self) -> str:
        """Return the uv tool command name.

        Returns:
            'uv'
        """
        return "uv"

    def group(self) -> str:
        """Return the badge group this tool belongs to.

        Returns:
            ``Group.TOOLING``
        """
        return Group.TOOLING

    def image_url(self) -> str:
        """Return the badge image URL for this tool.

        Returns:
            The URL of the badge image as a string.
        """
        return "https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json"

    def link_url(self) -> str:
        """Return the URL that the badge should link to for this tool.

        Returns:
            The URL of the project page as a string.
        """
        return "https://github.com/astral-sh/uv"

    def version_control_ignore_paths(self) -> tuple[str, ...]:
        """Return paths to ignore in version control."""
        return (".venv", "dist/")

    def package_root(self) -> Path:
        """Return the root directory of the project's main package.

        Combines ``source_root()`` and ``package_name()`` to produce the
        path where the importable package lives, e.g. ``src/my_project``.

        Returns:
            Path to the package root directory.
        """
        return self.source_root() / self.package_name()

    def package_name(self) -> str:
        """Return the importable Python package name.

        Converts the project name from kebab-case to snake_case, so a
        project named ``my-project`` has the package name ``my_project``.

        Returns:
            Python-importable package name derived from the project name.
        """
        return CLI.I.project_name_as_package_name(self.project_name())

    def project_name(self) -> str:
        """Return the project name.

        Derived from the name of the current working directory, which by
        convention matches the ``[project] name`` field in ``pyproject.toml``.

        Returns:
            Project name as the current directory's base name.
        """
        return Path.cwd().name

    def source_root(self) -> Path:
        """Return the source root directory.

        Returns:
            ``Path("src")``
        """
        return Path("src")

    def lock_file(self) -> Path:
        """Return the path to the uv lock file.

        Returns:
            ``Path("uv.lock")`` relative to the project root.
        """
        return Path("uv.lock")

    def build_system_requires(self) -> list[str]:
        """Return the ``[build-system].requires`` value for ``pyproject.toml``.

        Override this alongside ``build_backend`` if the project uses a
        different build back-end, for example ``["poetry-core"]`` for
        Poetry or ``["hatchling"]`` for Hatch.

        Returns:
            List of build-system requirements.
        """
        return ["uv_build"]

    def build_backend(self) -> str:
        """Return the ``[build-system].build-backend`` value for ``pyproject.toml``.

        Override this alongside ``build_system_requires`` if the project
        uses a different build back-end.

        Returns:
            Build-backend module path string.
        """
        return "uv_build"

    def no_auto_install_env_var(self) -> str:
        """Return the environment variable name that disables uv's auto-sync.

        uv implicitly runs ``uv sync`` before commands like ``uv run`` or
        ``uv version --bump`` when the virtual environment is out of date.
        Setting the returned variable to ``1`` disables that behaviour for
        the shell session.

        Returns:
            'UV_NO_SYNC'
        """
        return "UV_NO_SYNC"

    def dev_dependencies(self) -> tuple[str, ...]:
        """Return the dev dependencies required by this tool.

        uv is a system-level tool installed outside the Python virtual
        environment, so no Python dev dependency entry is needed.

        Returns:
            Empty tuple.
        """
        return ()

    def project_cmd_args(self, *args: str, cmd: Callable[..., Any]) -> Args:
        """Construct an ``Args`` object for running a project CLI subcommand.

        Converts the callable's ``__name__`` from snake_case to kebab-case to
        derive the subcommand name, then prepends the project name. For example,
        given a function named ``init_project``, this produces
        ``Args(("<project-name>", "init-project", *args))``.

        Args:
            *args: Additional arguments forwarded to the subcommand.
            cmd: Callable whose ``__name__`` is used as the subcommand name.

        Returns:
            Args for ``<project-name> <cmd-as-kebab> <args...>``.
        """
        cmd_name = snake_to_kebab_case(cmd.__name__)  # ty:ignore[unresolved-attribute]
        return Args((self.project_name(), cmd_name, *args))

    def init_project_args(self, *args: str) -> Args:
        """Construct ``Args`` for ``uv init``.

        Args:
            *args: Additional arguments for the init command.

        Returns:
            Args for ``uv init <args...>``.
        """
        return self.args("init", *args)

    def run_args(self, *args: str) -> Args:
        """Construct ``Args`` for ``uv run``.

        Args:
            *args: Command and arguments to run.

        Returns:
            Args for ``uv run <args...>``.
        """
        return self.args("run", *args)

    def add_dev_dependencies_args(self, *args: str) -> Args:
        """Construct ``Args`` for adding packages to the dev dependency group.

        Args:
            *args: Package names or additional ``uv add`` flags.

        Returns:
            Args for ``uv add --group dev <args...>``.
        """
        return self.args("add", "--group", "dev", *args)

    def add_dependencies_args(self, *args: str) -> Args:
        """Construct ``Args`` for adding production dependencies.

        Args:
            *args: Package names or additional ``uv add`` flags.

        Returns:
            Args for ``uv add <args...>``.
        """
        return self.args("add", *args)

    def install_dependencies_no_dev_args(self, *args: str) -> Args:
        """Construct ``Args`` for ``uv sync --no-group dev``.

        Synchronises the virtual environment against the lock file,
        installing or removing packages as needed without dev deps.

        Args:
            *args: Additional arguments for the sync command.

        Returns:
            Args for ``uv sync --no-group dev <args...>``.
        """
        return self.install_dependencies_args("--no-group", "dev", *args)

    def install_dependencies_args(self, *args: str) -> Args:
        """Construct ``Args`` for ``uv sync``.

        Synchronises the virtual environment against the lock file,
        installing or removing packages as needed.

        Args:
            *args: Additional arguments for the sync command.

        Returns:
            Args for ``uv sync <args...>``.
        """
        return self.args("sync", *args)

    def update_dependencies_args(self, *args: str) -> Args:
        """Construct ``Args`` for upgrading all locked dependency versions.

        Runs ``uv lock --upgrade``, which resolves the latest compatible
        versions and updates ``uv.lock`` without installing anything.

        Args:
            *args: Additional arguments for the lock command.

        Returns:
            Args for ``uv lock --upgrade <args...>``.
        """
        return self.args("lock", "--upgrade", *args)

    def update_self_args(self, *args: str) -> Args:
        """Construct ``Args`` for updating uv itself.

        Args:
            *args: Additional arguments for the self-update command.

        Returns:
            Args for ``uv self update <args...>``.
        """
        return self.args("self", "update", *args)

    def version_short_args(self, *args: str) -> Args:
        """Construct ``Args`` for reading the current project version as a bare string.

        Outputs only the version number without the project name, which makes
        it suitable for scripting and CI pipelines.

        Args:
            *args: Additional arguments for the version command.

        Returns:
            Args for ``uv version --short <args...>``.
        """
        return self.version_args("--short", *args)

    def version_args(self, *args: str) -> Args:
        """Construct ``Args`` for ``uv version``.

        Args:
            *args: Additional arguments for the version command.

        Returns:
            Args for ``uv version <args...>``.
        """
        return self.args("version", *args)

    def build_args(self, *args: str) -> Args:
        """Construct ``Args`` for ``uv build``.

        Args:
            *args: Additional arguments for the build command.

        Returns:
            Args for ``uv build <args...>``.
        """
        return self.args("build", *args)
