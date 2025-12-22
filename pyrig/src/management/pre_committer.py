"""Pre-commit utilities.

This module provides utilities for managing pre-commit hooks.
"""

from pyrig.src.management.base.base import Args, Tool


class PreCommitter(Tool):
    """Pre-commit code quality tool.

    Provides methods for constructing pre-commit command arguments for
    installing and running hooks.
    """

    @classmethod
    def name(cls) -> str:
        """Get the tool name.

        Returns:
            str: The string 'pre-commit'.
        """
        return "pre-commit"

    @classmethod
    def get_install_args(cls, *args: str) -> Args:
        """Construct pre-commit install command arguments.

        Args:
            *args: Additional arguments to append to the install command.

        Returns:
            Args: Command arguments for 'pre-commit install'.
        """
        return cls.get_args("install", *args)

    @classmethod
    def get_run_args(cls, *args: str) -> Args:
        """Construct pre-commit run command arguments.

        Args:
            *args: Additional arguments to append to the run command.

        Returns:
            Args: Command arguments for 'pre-commit run'.
        """
        return cls.get_args("run", *args)

    @classmethod
    def get_run_all_files_args(cls, *args: str) -> Args:
        """Construct pre-commit run command arguments for all files.

        Args:
            *args: Additional arguments to append to the run command.

        Returns:
            Args: Command arguments for 'pre-commit run --all-files'.
        """
        return cls.get_run_args("--all-files", *args)

    @classmethod
    def get_run_all_files_verbose_args(cls, *args: str) -> Args:
        """Construct pre-commit run command arguments for all files with verbose output.

        Args:
            *args: Additional arguments to append to the run command.

        Returns:
            Args: Command arguments for 'pre-commit run --all-files --verbose'.
        """
        return cls.get_run_all_files_args("--verbose", *args)
