"""UV package manager wrapper.

Provides type-safe wrapper for UV commands: init, sync, add, lock, build,
publish, run, version, self update.
UV is pyrig's primary package manager (Rust-based, replaces pip/virtualenv).

Example:
    >>> from pyrig.rig.tools.package_manager import PackageManager
    >>> PackageManager.I.install_dependencies_args().run()
    >>> PackageManager.I.add_dependencies_args("requests").run()
"""

from pyrig.rig.tools.base.base import Tool, ToolGroup
from pyrig.src.processes import Args


class PackageManager(Tool):
    """UV package manager wrapper.

    Constructs uv command arguments for package management operations.

    Operations:
        - Project setup: init, sync
        - Dependencies: add, lock --upgrade
        - Building: build, publish
        - Versioning: version, version --bump patch
        - Execution: run, run --no-group dev
        - Self-maintenance: self update

    Example:
        >>> PackageManager.I.install_dependencies_args().run()
        >>> PackageManager.I.add_dev_dependencies_args("ruff", "pytest").run()
    """

    def name(self) -> str:
        """Get tool name.

        Returns:
            'uv'
        """
        return "uv"

    def group(self) -> str:
        """Returns the group the tool belongs to.

        Returns:
            `ToolGroup.TOOLING`
        """
        return ToolGroup.TOOLING

    def badge_urls(self) -> tuple[str, str]:
        """Return the uv badge and project page URLs."""
        return (
            "https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json",
            "https://github.com/astral-sh/uv",
        )

    def dev_dependencies(self) -> list[str]:
        """Get development dependencies for this tool.

        UV is a system-level dependency installed outside the Python
        environment, so no dev dependencies are required.

        Returns:
            Empty list.
        """
        # uv is a system dependency, so we don't have a dev dependency for it
        return []

    def init_project_args(self, *args: str) -> Args:
        """Construct uv init arguments.

        Args:
            *args: Init command arguments.

        Returns:
            Args for 'uv init'.
        """
        return self.args("init", *args)

    def run_args(self, *args: str) -> Args:
        """Construct uv run arguments.

        Args:
            *args: Run command arguments.

        Returns:
            Args for 'uv run'.
        """
        return self.args("run", *args)

    def run_no_dev_args(self, *args: str) -> Args:
        """Construct uv run arguments without dev dependencies.

        Args:
            *args: Run command arguments.

        Returns:
            Args for 'uv run --no-group dev'.
        """
        return self.run_args("--no-group", "dev", *args)

    def add_dependencies_args(self, *args: str) -> Args:
        """Construct uv add arguments.

        Args:
            *args: Package names or add arguments.

        Returns:
            Args for 'uv add'.
        """
        return self.args("add", *args)

    def add_dev_dependencies_args(self, *args: str) -> Args:
        """Construct uv add arguments for dev dependencies.

        Args:
            *args: Package names or add arguments.

        Returns:
            Args for 'uv add --group dev'.
        """
        return self.args("add", "--group", "dev", *args)

    def install_dependencies_args(self, *args: str) -> Args:
        """Construct uv sync arguments.

        Args:
            *args: Sync command arguments.

        Returns:
            Args for 'uv sync'.
        """
        return self.args("sync", *args)

    def install_dependencies_no_dev_args(self, *args: str) -> Args:
        """Construct uv sync arguments without dev dependencies.

        Args:
            *args: Sync command arguments.

        Returns:
            Args for 'uv sync --no-group dev'.
        """
        return self.install_dependencies_args("--no-group", "dev", *args)

    def update_dependencies_args(self, *args: str) -> Args:
        """Construct uv lock arguments for updating dependencies.

        Args:
            *args: Lock command arguments.

        Returns:
            Args for 'uv lock --upgrade'.
        """
        return self.args("lock", "--upgrade", *args)

    def update_self_args(self, *args: str) -> Args:
        """Construct uv self update arguments.

        Args:
            *args: Self update arguments.

        Returns:
            Args for 'uv self update'.
        """
        return self.args("self", "update", *args)

    def patch_version_args(self, *args: str) -> Args:
        """Construct uv version arguments for patch bump.

        Args:
            *args: Version command arguments.

        Returns:
            Args for 'uv version --bump patch'.
        """
        return self.args("version", "--bump", "patch", *args)

    def build_args(self, *args: str) -> Args:
        """Construct uv build arguments.

        Args:
            *args: Build command arguments.

        Returns:
            Args for 'uv build'.
        """
        return self.args("build", *args)

    def publish_args(self, *args: str, token: str) -> Args:
        """Construct uv publish arguments with token.

        Args:
            *args: Additional publish command arguments.
            token: Authentication token (keyword-only).

        Returns:
            Args for 'uv publish --token <token>'.
        """
        return self.args("publish", "--token", token, *args)

    def version_args(self, *args: str) -> Args:
        """Construct uv version arguments.

        Args:
            *args: Version command arguments.

        Returns:
            Args for 'uv version'.
        """
        return self.args("version", *args)

    def version_short_args(self, *args: str) -> Args:
        """Construct uv version arguments with short output.

        Args:
            *args: Version command arguments.

        Returns:
            Args for 'uv version --short'.
        """
        return self.version_args("--short", *args)

    def no_auto_install_env_var(self) -> str:
        """Get environment variable name for disabling automatic dependency syncing.

        UV normally runs ``uv sync`` implicitly before commands like
        ``uv run`` or ``uv version --bump`` when the venv is out of date.
        Setting the returned env var to ``1`` disables that behaviour for
        the shell session.

        Returns:
            'UV_NO_SYNC'
        """
        return "UV_NO_SYNC"

    def build_system_requires(self) -> list[str]:
        """Get build-system requires for pyproject.toml.

        If uv is not used but replaced by poetry for example, this should be
        overridden to return ["poetry-core"].
        Or if setuptools or hatch is preferred, that should be returned instead.

        Returns:
            List of dependencies for [build-system].requires.
        """
        return ["uv_build"]

    def build_backend(self) -> str:
        """Get build-backend for pyproject.toml.

        Should be overridden if build_system_requires is overridden and vice versa.

        Returns:
            Build backend for [build-system].build-backend.
        """
        return "uv_build"
