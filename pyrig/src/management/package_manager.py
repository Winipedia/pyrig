"""UV package manager utilities.

This module provides utilities for managing Python project dependencies
using the uv package manager. It centralizes command construction for
common dependency management tasks.
"""

from pyrig.src.management.base.base import Args, Tool


class PackageManager(Tool):
    """UV package manager tool for Python projects.

    Provides methods for constructing uv command arguments for package
    management, project initialization, building, and publishing.
    """

    @classmethod
    def name(cls) -> str:
        """Get the tool name.

        Returns:
            str: The string 'uv'.
        """
        return "uv"

    @classmethod
    def get_init_project_args(cls, *args: str) -> Args:
        """Construct uv init command arguments for project initialization.

        Args:
            *args: Additional arguments to append to the init command.

        Returns:
            Args: Command arguments for 'uv init'.
        """
        return cls.get_args("init", *args)

    @classmethod
    def get_run_args(cls, *args: str) -> Args:
        """Construct uv run command arguments.

        Args:
            *args: Additional arguments to append to the run command.

        Returns:
            Args: Command arguments for 'uv run'.
        """
        return cls.get_args("run", *args)

    @classmethod
    def get_add_dependencies_args(cls, *args: str) -> Args:
        """Construct uv add command arguments for dependencies.

        Args:
            *args: Package names or additional arguments for the add command.

        Returns:
            Args: Command arguments for 'uv add'.
        """
        return cls.get_args("add", *args)

    @classmethod
    def get_add_dev_dependencies_args(cls, *args: str) -> Args:
        """Construct uv add command arguments for dev dependencies.

        Args:
            *args: Package names or additional arguments for the add command.

        Returns:
            Args: Command arguments for 'uv add --group dev'.
        """
        return cls.get_args("add", "--group", "dev", *args)

    @classmethod
    def get_install_dependencies_args(cls, *args: str) -> Args:
        """Construct uv sync command arguments for installing dependencies.

        Args:
            *args: Additional arguments to append to the sync command.

        Returns:
            Args: Command arguments for 'uv sync'.
        """
        return cls.get_args("sync", *args)

    @classmethod
    def get_update_dependencies_args(cls, *args: str) -> Args:
        """Construct uv lock command arguments for updating dependencies.

        Args:
            *args: Additional arguments to append to the lock command.

        Returns:
            Args: Command arguments for 'uv lock --upgrade'.
        """
        return cls.get_args("lock", "--upgrade", *args)

    @classmethod
    def get_update_self_args(cls, *args: str) -> Args:
        """Construct uv self update command arguments.

        Args:
            *args: Additional arguments to append to the self update command.

        Returns:
            Args: Command arguments for 'uv self update'.
        """
        return cls.get_args("self", "update", *args)

    @classmethod
    def get_patch_version_args(cls, *args: str) -> Args:
        """Construct uv version command arguments for patch version bump.

        Args:
            *args: Additional arguments to append to the version command.

        Returns:
            Args: Command arguments for 'uv version --bump patch'.
        """
        return cls.get_args("version", "--bump", "patch", *args)

    @classmethod
    def get_build_args(cls, *args: str) -> Args:
        """Construct uv build command arguments.

        Args:
            *args: Additional arguments to append to the build command.

        Returns:
            Args: Command arguments for 'uv build'.
        """
        return cls.get_args("build", *args)

    @classmethod
    def get_publish_args(cls, token: str, *args: str) -> Args:
        """Construct uv publish command arguments with authentication token.

        Args:
            token: Authentication token for publishing.
            *args: Additional arguments to append to the publish command.

        Returns:
            Args: Command arguments for 'uv publish --token <token>'.
        """
        return cls.get_args("publish", "--token", token, *args)

    @classmethod
    def get_version_args(cls, *args: str) -> Args:
        """Construct uv version command arguments.

        Args:
            *args: Additional arguments to append to the version command.

        Returns:
            Args: Command arguments for 'uv version'.
        """
        return cls.get_args("version", *args)

    @classmethod
    def get_version_short_args(cls, *args: str) -> Args:
        """Construct uv version command arguments with short output format.

        Args:
            *args: Additional arguments to append to the version command.

        Returns:
            Args: Command arguments for 'uv version --short'.
        """
        return cls.get_version_args("--short", *args)
