"""Prek hook manager wrapper.

Provides type-safe wrapper for prek commands (install, run).
Enforces code quality standards via linters, formatters, and checks.

Example:
    >>> from pyrig.rig.tools.pre_committer import PreCommitter
    >>> PreCommitter.L.get_install_args().run()
    >>> PreCommitter.L.get_run_all_files_args().run()
"""

from pyrig.rig.tools.base.base import Tool, ToolGroup
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
    def group(cls) -> str:
        """Returns the group the tools belongs to.

        E.g. testing, tool, code-quality etc...
        """
        return ToolGroup.CODE_QUALITY

    @classmethod
    def badge_urls(cls) -> tuple[str, str]:
        """Returns the badge and connected page."""
        return (
            "https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/j178/prek/master/docs/assets/badge-v0.json",
            "https://github.com/j178/prek",
        )

    @classmethod
    def get_install_args(cls, *args: str) -> Args:
        """Construct prek install arguments.

        Args:
            *args: Install command arguments.

        Returns:
            Args for 'prek install'.
        """
        return cls.build_args("install", *args)

    @classmethod
    def get_run_args(cls, *args: str) -> Args:
        """Construct prek run arguments.

        Args:
            *args: Run command arguments.

        Returns:
            Args for 'prek run'.
        """
        return cls.build_args("run", *args)

    @classmethod
    def get_run_all_files_args(cls, *args: str) -> Args:
        """Construct prek run arguments for all files.

        Args:
            *args: Run command arguments.

        Returns:
            Args for 'prek run --all-files'.
        """
        return cls.get_run_args("--all-files", *args)
