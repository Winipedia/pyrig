"""Base classes for type-safe command-line argument construction.

Provides `Args` (executable command tuples) and `Tool` (base for tool wrappers).

Design pattern:
    1. Each tool (uv, git, pytest) is a `Tool` subclass
    2. Tool methods return `Args` objects (command argument tuples)
    3. `Args` objects execute directly or convert to strings
    4. All command construction centralized and testable

Benefits:
    - Type safety: Arguments validated at construction
    - Composability: Args combined and extended
    - Testability: Command construction tested without execution
    - Discoverability: IDE autocomplete shows available commands

Example:
    >>> from pyrig.src.management.package_manager import PackageManager
    >>> args = PackageManager.get_install_dependencies_args()
    >>> print(args)
    uv sync
    >>> args.run()
    CompletedProcess(...)
"""

import logging
from abc import ABC, abstractmethod
from subprocess import CompletedProcess  # nosec: B404
from typing import Any

from pyrig.src.os.os import run_subprocess

logger = logging.getLogger(__name__)


class Args(tuple[str, ...]):
    """Command-line arguments container with execution capabilities.

    Immutable tuple subclass representing command arguments.
    Return type for all Tool methods.

    Methods:
        __str__: Convert to space-separated string
        run: Execute via subprocess

    Example:
        >>> args = Args(("uv", "sync"))
        >>> print(args)
        uv sync
        >>> args.run()
        CompletedProcess(...)
    """

    __slots__ = ()

    def __str__(self) -> str:
        """Convert to space-separated string.

        Returns:
            Space-separated command string.
        """
        return " ".join(self)

    def run(self, *args: str, **kwargs: Any) -> CompletedProcess[Any]:
        """Execute command via subprocess.

        Args:
            *args: Additional arguments appended to command.
            **kwargs: Keyword arguments passed to run_subprocess
                (check, capture_output, cwd, etc.).

        Returns:
            CompletedProcess from subprocess execution.

        Raises:
            subprocess.CalledProcessError: If check=True and command fails.
        """
        return run_subprocess(self, *args, **kwargs)


class Tool(ABC):
    """Abstract base for tool command argument construction.

    Provides consistent interface for constructing command-line arguments.
    Subclasses implement `name` and provide `get_*_args` methods.

    Pattern:
        - Each tool method returns `Args` object
        - Method names indicate command being constructed
        - Arguments validated at construction
        - Commands testable without execution

    Example:
        >>> class MyTool(Tool):
        ...     @classmethod
        ...     def name(cls) -> str:
        ...         return "mytool"
        ...     @classmethod
        ...     def get_build_args(cls, *args: str) -> Args:
        ...         return cls.get_args("build", *args)
        >>> MyTool.get_build_args("--verbose")
        Args(('mytool', 'build', '--verbose'))
    """

    @classmethod
    @abstractmethod
    def name(cls) -> str:
        """Get tool command name.

        Returns:
            Tool command name (e.g., "git", "uv", "pytest").
        """

    @classmethod
    def get_args(cls, *args: str) -> Args:
        """Construct command arguments with tool name prepended.

        Args:
            *args: Command arguments.

        Returns:
            Args object with tool name and arguments.

        Note:
            Subclasses provide higher-level methods calling this internally.
        """
        return Args((cls.name(), *args))
