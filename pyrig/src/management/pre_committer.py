"""Pre-commit hook manager wrapper for code quality enforcement.

This module provides a type-safe wrapper for pre-commit hook management commands.
The `PreCommitter` class constructs pre-commit command arguments for installing
git hooks and running code quality checks.

Pre-commit is used in pyrig projects to enforce code quality standards before
commits are made. It runs linters, formatters, and other checks automatically.

Example:
    >>> from pyrig.src.management.pre_committer import PreCommitter
    >>> # Install pre-commit hooks
    >>> install_args = PreCommitter.get_install_args()
    >>> install_args.run()
    >>>
    >>> # Run hooks on all files
    >>> run_args = PreCommitter.get_run_all_files_args()
    >>> run_args.run()

See Also:
    pyrig.src.management.base.base.Tool: Base class for tool wrappers
    pyrig.dev.configs.pre_commit: Pre-commit configuration management
"""

from pyrig.src.management.base.base import Args, Tool


class PreCommitter(Tool):
    """Pre-commit hook manager tool wrapper.

    Provides methods for constructing pre-commit command arguments for installing
    git hooks and running code quality checks. Pre-commit runs configured hooks
    (linters, formatters, type checkers) automatically before commits.

    The class provides methods for:
        - **Installation**: Install hooks into git
        - **Execution**: Run hooks on staged files or all files
        - **Verbosity**: Control output detail level

    All methods return `Args` objects that can be executed via `.run()` or
    converted to strings for display.

    Example:
        >>> # Install hooks
        >>> PreCommitter.get_install_args().run()
        >>>
        >>> # Run on all files with verbose output
        >>> PreCommitter.get_run_all_files_verbose_args().run()

    See Also:
        pyrig.src.management.base.base.Tool: Base class
        pyrig.dev.configs.pre_commit.PreCommitConfigFile: Hook configuration
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
