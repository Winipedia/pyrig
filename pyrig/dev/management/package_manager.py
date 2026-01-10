"""UV package manager wrapper.

Provides type-safe wrapper for UV commands: init, sync, add, build, publish, version.
UV is pyrig's primary package manager (Rust-based, replaces pip/virtualenv).

Example:
    >>> from pyrig.dev.management.package_manager import PackageManager
    >>> PackageManager.L.get_install_dependencies_args().run()
    >>> PackageManager.L.get_add_dependencies_args("requests").run()
"""

from pyrig.dev.management.base.base import Tool
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
        >>> PackageManager.L.get_install_dependencies_args().run()
        >>> PackageManager.L.get_add_dev_dependencies_args("pyrig-dev").run()
    """

    @classmethod
    def name(cls) -> str:
        """Get tool name.

        Returns:
            'uv'
        """
        return "uv"

    @classmethod
    def get_init_project_args(cls, *args: str) -> Args:
        """Construct uv init arguments.

        Args:
            *args: Init command arguments.

        Returns:
            Args for 'uv init'.
        """
        return cls.get_args("init", *args)

    @classmethod
    def get_run_args(cls, *args: str) -> Args:
        """Construct uv run arguments.

        Args:
            *args: Run command arguments.

        Returns:
            Args for 'uv run'.
        """
        return cls.get_args("run", *args)

    @classmethod
    def get_run_no_dev_args(cls, *args: str) -> Args:
        """Construct uv run arguments without dev dependencies.

        Args:
            *args: Run command arguments.

        Returns:
            Args for 'uv run --no-group dev'.
        """
        return cls.get_run_args("--no-group", "dev", *args)

    @classmethod
    def get_add_dependencies_args(cls, *args: str) -> Args:
        """Construct uv add arguments.

        Args:
            *args: Package names or add arguments.

        Returns:
            Args for 'uv add'.
        """
        return cls.get_args("add", *args)

    @classmethod
    def get_add_dev_dependencies_args(cls, *args: str) -> Args:
        """Construct uv add arguments for dev dependencies.

        Args:
            *args: Package names or add arguments.

        Returns:
            Args for 'uv add --group dev'.
        """
        return cls.get_args("add", "--group", "dev", *args)

    @classmethod
    def get_install_dependencies_args(cls, *args: str) -> Args:
        """Construct uv sync arguments.

        Args:
            *args: Sync command arguments.

        Returns:
            Args for 'uv sync'.
        """
        return cls.get_args("sync", *args)

    @classmethod
    def get_install_dependencies_no_dev_args(cls, *args: str) -> Args:
        """Construct uv sync arguments without dev dependencies.

        Args:
            *args: Sync command arguments.

        Returns:
            Args for 'uv sync --no-group dev'.
        """
        return cls.get_install_dependencies_args("--no-group", "dev", *args)

    @classmethod
    def get_update_dependencies_args(cls, *args: str) -> Args:
        """Construct uv lock arguments for updating dependencies.

        Args:
            *args: Lock command arguments.

        Returns:
            Args for 'uv lock --upgrade'.
        """
        return cls.get_args("lock", "--upgrade", *args)

    @classmethod
    def get_update_self_args(cls, *args: str) -> Args:
        """Construct uv self update arguments.

        Args:
            *args: Self update arguments.

        Returns:
            Args for 'uv self update'.
        """
        return cls.get_args("self", "update", *args)

    @classmethod
    def get_patch_version_args(cls, *args: str) -> Args:
        """Construct uv version arguments for patch bump.

        Args:
            *args: Version command arguments.

        Returns:
            Args for 'uv version --bump patch'.
        """
        return cls.get_args("version", "--bump", "patch", *args)

    @classmethod
    def get_build_args(cls, *args: str) -> Args:
        """Construct uv build arguments.

        Args:
            *args: Build command arguments.

        Returns:
            Args for 'uv build'.
        """
        return cls.get_args("build", *args)

    @classmethod
    def get_publish_args(cls, *args: str, token: str) -> Args:
        """Construct uv publish arguments with token.

        Args:
            *args: Additional publish command arguments.
            token: Authentication token (keyword-only).

        Returns:
            Args for 'uv publish --token <token>'.
        """
        return cls.get_args("publish", "--token", token, *args)

    @classmethod
    def get_version_args(cls, *args: str) -> Args:
        """Construct uv version arguments.

        Args:
            *args: Version command arguments.

        Returns:
            Args for 'uv version'.
        """
        return cls.get_args("version", *args)

    @classmethod
    def get_version_short_args(cls, *args: str) -> Args:
        """Construct uv version arguments with short output.

        Args:
            *args: Version command arguments.

        Returns:
            Args for 'uv version --short'.
        """
        return cls.get_version_args("--short", *args)
