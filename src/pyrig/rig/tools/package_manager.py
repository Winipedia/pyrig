"""UV package manager wrapper.

Wraps uv commands as type-safe ``Args`` objects for use across pyrig,
covering project setup, dependency management, versioning, builds, and publishing.
"""

from collections.abc import Callable
from pathlib import Path
from typing import Any

from pyrig.core.strings import (
    kebab_to_snake_case,
    snake_to_kebab_case,
)
from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Tool, ToolGroup


class PackageManager(Tool):
    """uv package manager wrapper.

    Each method constructs a type-safe ``Args`` object for a specific uv
    command. Call ``.run()`` on the result to execute it, or convert it to
    a string to embed in CI workflow scripts.

    Subclass and override ``build_system_requires``, ``build_backend``,
    ``source_root``, or ``dev_dependencies`` to adapt pyrig to a different
    build back-end or project layout.

    Example:
        >>> PackageManager.I.install_dependencies_args().run()
        >>> PackageManager.I.add_dev_dependencies_args("ruff", "pytest").run()
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
            ``ToolGroup.TOOLING``
        """
        return ToolGroup.TOOLING

    def badge_urls(self) -> tuple[str, str]:
        """Return the uv badge image URL and project page URL.

        Returns:
            Tuple of (badge_image_url, project_page_url).
        """
        return (
            "https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json",
            "https://github.com/astral-sh/uv",
        )

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
        return kebab_to_snake_case(self.project_name())

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

    def container_image(self) -> tuple[str, str, str]:
        """Return the container image coordinates for copying uv.

        Used when generating a ``Containerfile`` to add a
        ``COPY --from=<image> <src> <dst>`` directive that installs uv
        into the container image.

        Returns:
            Tuple of (image_name, path_in_source_image, path_in_target_image).
        """
        return "ghcr.io/astral-sh/uv:latest", "/uv", "/usr/local/bin/uv"

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
        # uv is a system dependency, so we don't have a dev dependency for it
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

    def run_no_dev_args(self, *args: str) -> Args:
        """Construct ``Args`` for ``uv run`` with the dev dependency group excluded.

        Useful for validating that the project works without dev tooling,
        for example in a production-like smoke test.

        Args:
            *args: Command and arguments to run.

        Returns:
            Args for ``uv run --no-group dev <args...>``.
        """
        return self.run_args("--no-group", "dev", *args)

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
        """Construct ``Args`` for syncing dependencies without the dev group.

        Useful in containers or production environments where dev tooling
        should not be installed.

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

    def patch_version_args(self, *args: str) -> Args:
        """Construct ``Args`` for bumping the patch segment of the project version.

        Increments the third component of the semver string (e.g.
        ``1.2.3`` → ``1.2.4``) and writes the new version back to
        ``pyproject.toml``.

        Args:
            *args: Additional arguments for the version command.

        Returns:
            Args for ``uv version --bump patch <args...>``.
        """
        return self.args("version", "--bump", "patch", *args)

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

    def publish_args(self, *args: str, token: str) -> Args:
        """Construct ``Args`` for publishing the package to PyPI.

        Args:
            *args: Additional arguments for the publish command.
            token: PyPI authentication token (keyword-only).

        Returns:
            Args for ``uv publish --token <token> <args...>``.
        """
        return self.args("publish", "--token", token, *args)
