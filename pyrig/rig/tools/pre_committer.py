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

    def name(self) -> str:
        """Get tool name.

        Returns:
            'prek'
        """
        return "prek"

    def group(self) -> str:
        """Get tool group.

        Returns:
            'code-quality'
        """
        return ToolGroup.CODE_QUALITY

    def badge_urls(self) -> tuple[str, str]:
        """Get prek badge image URL and project page URL."""
        return (
            "https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/j178/prek/master/docs/assets/badge-v0.json",
            "https://github.com/j178/prek",
        )

    def install_args(self, *args: str) -> Args:
        """Construct prek install arguments.

        Args:
            *args: Install command arguments.

        Returns:
            Args for 'prek install'.
        """
        return self.args("install", *args)

    def run_args(self, *args: str) -> Args:
        """Construct prek run arguments.

        Args:
            *args: Run command arguments.

        Returns:
            Args for 'prek run'.
        """
        return self.args("run", *args)

    def run_all_files_args(self, *args: str) -> Args:
        """Construct prek run arguments for all files.

        Args:
            *args: Run command arguments.

        Returns:
            Args for 'prek run --all-files'.
        """
        return self.run_args("--all-files", *args)
