"""UV package manager wrapper.

Provides type-safe wrapper for UV commands: init, sync, add, build, publish, version.
UV is pyrig's primary package manager (Rust-based, replaces pip/virtualenv).

Example:
    >>> from pyrig.rig.tools.package_manager import PackageManager
    >>> PackageManager.L.install_dependencies_args().run()
    >>> PackageManager.L.add_dependencies_args("requests").run()
"""

from pyrig.rig.tools.base.base import Tool, ToolGroup
from pyrig.src.processes import Args


class PackageManager(Tool):
    """UV package manager wrapper.

    Constructs uv command arguments for package management operations.

    Operations:
        - Project setup: init, sync
        - Dependencies: add, update
        - Building: build, publish
        - Versioning: version bumping
        - Execution: run commands

    Example:
        >>> PackageManager.L.install_dependencies_args().run()
        >>> PackageManager.L.add_dev_dependencies_args("ruff", "pytest").run()
    """

    @classmethod
    def name(cls) -> str:
        """Get tool name.

        Returns:
            'uv'
        """
        return "uv"

    @classmethod
    def group(cls) -> str:
        """Returns the group the tools belongs to.

        E.g. testing, tool, code-quality etc...
        """
        return ToolGroup.TOOLING

    @classmethod
    def badge_urls(cls) -> tuple[str, str]:
        """Returns the badge urls for uv."""
        return (
            "https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json",
            "https://github.com/astral-sh/uv",
        )

    @classmethod
    def dev_dependencies(cls) -> list[str]:
        """Get tool dependencies.

        Returns:
            List of tool dependencies.
        """
        # uv is a system dependency, so we don't have a dev dependency for it
        return []

    @classmethod
    def init_project_args(cls, *args: str) -> Args:
        """Construct uv init arguments.

        Args:
            *args: Init command arguments.

        Returns:
            Args for 'uv init'.
        """
        return cls.args("init", *args)

    @classmethod
    def run_args(cls, *args: str) -> Args:
        """Construct uv run arguments.

        Args:
            *args: Run command arguments.

        Returns:
            Args for 'uv run'.
        """
        return cls.args("run", *args)

    @classmethod
    def run_no_dev_args(cls, *args: str) -> Args:
        """Construct uv run arguments without dev dependencies.

        Args:
            *args: Run command arguments.

        Returns:
            Args for 'uv run --no-group dev'.
        """
        return cls.run_args("--no-group", "dev", *args)

    @classmethod
    def add_dependencies_args(cls, *args: str) -> Args:
        """Construct uv add arguments.

        Args:
            *args: Package names or add arguments.

        Returns:
            Args for 'uv add'.
        """
        return cls.args("add", *args)

    @classmethod
    def add_dev_dependencies_args(cls, *args: str) -> Args:
        """Construct uv add arguments for dev dependencies.

        Args:
            *args: Package names or add arguments.

        Returns:
            Args for 'uv add --group dev'.
        """
        return cls.args("add", "--group", "dev", *args)

    @classmethod
    def install_dependencies_args(cls, *args: str) -> Args:
        """Construct uv sync arguments.

        Args:
            *args: Sync command arguments.

        Returns:
            Args for 'uv sync'.
        """
        return cls.args("sync", *args)

    @classmethod
    def install_dependencies_no_dev_args(cls, *args: str) -> Args:
        """Construct uv sync arguments without dev dependencies.

        Args:
            *args: Sync command arguments.

        Returns:
            Args for 'uv sync --no-group dev'.
        """
        return cls.install_dependencies_args("--no-group", "dev", *args)

    @classmethod
    def update_dependencies_args(cls, *args: str) -> Args:
        """Construct uv lock arguments for updating dependencies.

        Args:
            *args: Lock command arguments.

        Returns:
            Args for 'uv lock --upgrade'.
        """
        return cls.args("lock", "--upgrade", *args)

    @classmethod
    def update_self_args(cls, *args: str) -> Args:
        """Construct uv self update arguments.

        Args:
            *args: Self update arguments.

        Returns:
            Args for 'uv self update'.
        """
        return cls.args("self", "update", *args)

    @classmethod
    def patch_version_args(cls, *args: str) -> Args:
        """Construct uv version arguments for patch bump.

        Args:
            *args: Version command arguments.

        Returns:
            Args for 'uv version --bump patch'.
        """
        return cls.args("version", "--bump", "patch", *args)

    @classmethod
    def build_args(cls, *args: str) -> Args:
        """Construct uv build arguments.

        Args:
            *args: Build command arguments.

        Returns:
            Args for 'uv build'.
        """
        return cls.args("build", *args)

    @classmethod
    def publish_args(cls, *args: str, token: str) -> Args:
        """Construct uv publish arguments with token.

        Args:
            *args: Additional publish command arguments.
            token: Authentication token (keyword-only).

        Returns:
            Args for 'uv publish --token <token>'.
        """
        return cls.args("publish", "--token", token, *args)

    @classmethod
    def version_args(cls, *args: str) -> Args:
        """Construct uv version arguments.

        Args:
            *args: Version command arguments.

        Returns:
            Args for 'uv version'.
        """
        return cls.args("version", *args)

    @classmethod
    def version_short_args(cls, *args: str) -> Args:
        """Construct uv version arguments with short output.

        Args:
            *args: Version command arguments.

        Returns:
            Args for 'uv version --short'.
        """
        return cls.version_args("--short", *args)

    @classmethod
    def no_auto_install_env_var(cls) -> str:
        """Get environment variable name for disabling auto-install.

        E.g. uv sync automatically if the venv is not in sync with the lock file
        if you do uv run or uv version --bump or similar.
        We do not want that in some cases so we can set this environment variable
        to disable that behaviour globally for the shell session.

        Returns:
            'UV_NO_SYNC'
        """
        return "UV_NO_SYNC"

    @classmethod
    def build_system_requires(cls) -> list[str]:
        """Get build-system requires for pyproject.toml.

        If uv is not used but replaced by poetry for example, this should be
        overridden to return ["poetry-core"].
        Or if setuptools or hatch is preferred, that should be returned instead.

        Returns:
            List of dependencies for [build-system].requires.
        """
        return ["uv_build"]

    @classmethod
    def build_backend(cls) -> str:
        """Get build-backend for pyproject.toml.

        Should be overridden if build_system_requires is overridden and vice versa.

        Returns:
            Build backend for [build-system].build-backend.
        """
        return "uv_build"
