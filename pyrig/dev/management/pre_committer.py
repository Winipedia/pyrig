"""Pre-commit hook manager wrapper.

Provides type-safe wrapper for pre-commit commands (install, run).
Enforces code quality standards via linters, formatters, and checks.

Example:
    >>> from pyrig.dev.management.pre_committer import PreCommitter
    >>> PreCommitter.L.get_install_args().run()
    >>> PreCommitter.L.get_run_all_files_args().run()
"""

from pyrig.dev.management.base.base import Tool
from pyrig.src.processes import Args


class PreCommitter(Tool):
    """Pre-commit hook manager wrapper.

    Constructs pre-commit command arguments for installing hooks and running checks.

    Operations:
        - Installation: Install hooks into git
        - Execution: Run hooks on staged/all files
        - Verbosity: Control output detail

    Example:
        >>> PreCommitter.L.get_install_args().run()
        >>> PreCommitter.L.get_run_all_files_verbose_args().run()
    """

    @classmethod
    def name(cls) -> str:
        """Get tool name.

        Returns:
            'pre-commit'
        """
        return "pre-commit"

    @classmethod
    def get_install_args(cls, *args: str) -> Args:
        """Construct pre-commit install arguments.

        Args:
            *args: Install command arguments.

        Returns:
            Args for 'pre-commit install'.
        """
        return cls.get_args("install", *args)

    @classmethod
    def get_run_args(cls, *args: str) -> Args:
        """Construct pre-commit run arguments.

        Args:
            *args: Run command arguments.

        Returns:
            Args for 'pre-commit run'.
        """
        return cls.get_args("run", *args)

    @classmethod
    def get_run_all_files_args(cls, *args: str) -> Args:
        """Construct pre-commit run arguments for all files.

        Args:
            *args: Run command arguments.

        Returns:
            Args for 'pre-commit run --all-files'.
        """
        return cls.get_run_args("--all-files", *args)

    @classmethod
    def get_run_all_files_verbose_args(cls, *args: str) -> Args:
        """Construct pre-commit run arguments for all files with verbose output.

        Args:
            *args: Run command arguments.

        Returns:
            Args for 'pre-commit run --all-files --verbose'.
        """
        return cls.get_run_all_files_args("--verbose", *args)
