"""Prek hook manager wrapper.

Provides type-safe wrapper for prek commands (install, run).
Enforces code quality standards via linters, formatters, and checks.

Example:
    >>> from pyrig.rig.tools.pre_committer import PreCommitter
    >>> PreCommitter.L.get_install_args().run()
    >>> PreCommitter.L.get_run_all_files_args().run()
"""

from pyrig.rig.tools.base.base import Tool
from pyrig.src.processes import Args


class PreCommitter(Tool):
    """Prek hook manager wrapper.

    Constructs prek command arguments for installing hooks and running checks.

    Operations:
        - Installation: Install hooks into git
        - Execution: Run hooks on staged/all files
        - Verbosity: Control output detail

    Example:
        >>> PreCommitter.L.get_install_args().run()
        >>> PreCommitter.L.get_run_all_files_args().run()
    """

    @classmethod
    def name(cls) -> str:
        """Get tool name.

        Returns:
            'prek'
        """
        return "prek"

    @classmethod
    def get_install_args(cls, *args: str) -> Args:
        """Construct prek install arguments.

        Args:
            *args: Install command arguments.

        Returns:
            Args for 'prek install'.
        """
        return cls.get_args("install", *args)

    @classmethod
    def get_run_args(cls, *args: str) -> Args:
        """Construct prek run arguments.

        Args:
            *args: Run command arguments.

        Returns:
            Args for 'prek run'.
        """
        return cls.get_args("run", *args)

    @classmethod
    def get_run_all_files_args(cls, *args: str) -> Args:
        """Construct prek run arguments for all files.

        Args:
            *args: Run command arguments.

        Returns:
            Args for 'prek run --all-files'.
        """
        return cls.get_run_args("--all-files", *args)
