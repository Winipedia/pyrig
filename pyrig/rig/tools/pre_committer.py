"""Prek hook manager wrapper.

Provides type-safe wrapper for prek commands (install, run).
Enforces code quality standards via linters, formatters, and checks.

Example:
    >>> from pyrig.rig.tools.pre_committer import PreCommitter
    >>> PreCommitter.I.install_args().run()
    >>> PreCommitter.I.run_all_files_args().run()
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
        >>> PreCommitter.I.install_args().run()
        >>> PreCommitter.I.run_all_files_args().run()
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
        """Get tool group.

        Returns:
            'code-quality'
        """
        return ToolGroup.CODE_QUALITY

    @classmethod
    def badge_urls(cls) -> tuple[str, str]:
        """Get prek badge image URL and project page URL."""
        return (
            "https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/j178/prek/master/docs/assets/badge-v0.json",
            "https://github.com/j178/prek",
        )

    @classmethod
    def install_args(cls, *args: str) -> Args:
        """Construct prek install arguments.

        Args:
            *args: Install command arguments.

        Returns:
            Args for 'prek install'.
        """
        return cls.args("install", *args)

    @classmethod
    def run_args(cls, *args: str) -> Args:
        """Construct prek run arguments.

        Args:
            *args: Run command arguments.

        Returns:
            Args for 'prek run'.
        """
        return cls.args("run", *args)

    @classmethod
    def run_all_files_args(cls, *args: str) -> Args:
        """Construct prek run arguments for all files.

        Args:
            *args: Run command arguments.

        Returns:
            Args for 'prek run --all-files'.
        """
        return cls.run_args("--all-files", *args)
