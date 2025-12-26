"""Base classes for type-safe command-line argument construction.

This module provides the foundational classes for pyrig's tool wrapper system.
The `Args` and `Tool` classes enable type-safe, composable construction of
command-line arguments for development tools.

The design pattern:
    1. Each tool (uv, git, pytest, etc.) is a `Tool` subclass
    2. Tool methods return `Args` objects (tuples of command arguments)
    3. `Args` objects can be executed directly or converted to strings
    4. All command construction is centralized and testable

This approach provides several benefits:
    - **Type safety**: Arguments are validated at construction time
    - **Composability**: Args can be combined and extended
    - **Testability**: Command construction can be tested without execution
    - **Discoverability**: IDE autocomplete shows available commands

Example:
    >>> from pyrig.src.management.package_manager import PackageManager
    >>> args = PackageManager.get_install_dependencies_args()
    >>> print(args)
    uv sync
    >>> args.run()  # Execute the command
    CompletedProcess(...)

See Also:
    pyrig.src.management.package_manager.PackageManager: UV package manager
    pyrig.src.management.version_controller.VersionController: Git wrapper
    pyrig.src.os.os.run_subprocess: Subprocess execution
"""

import logging
from abc import ABC, abstractmethod
from subprocess import CompletedProcess  # nosec: B404
from typing import Any

from pyrig.src.os.os import run_subprocess

logger = logging.getLogger(__name__)


class Args(tuple[str, ...]):
    """Command-line arguments container with execution capabilities.

    A tuple subclass that represents command-line arguments and provides
    convenient methods for string representation and subprocess execution.
    This is the return type for all Tool methods.

    The class is immutable (being a tuple subclass) and can be used anywhere
    a tuple of strings is expected. It adds two convenience methods:
        - `__str__`: Convert to space-separated string for display
        - `run`: Execute the command via subprocess

    Attributes:
        Inherits all tuple attributes. No additional instance attributes.

    Example:
        Creating and using Args::

            >>> args = Args(("uv", "sync"))
            >>> print(args)
            uv sync
            >>> args[0]
            'uv'
            >>> len(args)
            2

        Executing commands::

            >>> args = Args(("echo", "hello"))
            >>> result = args.run()
            >>> result.returncode
            0

        Combining with other arguments::

            >>> base = Args(("git", "commit"))
            >>> full = Args((*base, "-m", "message"))
            >>> print(full)
            git commit -m message

    Note:
        The `run` method passes all arguments through to `run_subprocess`,
        so you can use any subprocess options (check, capture_output, etc.).

    See Also:
        Tool: Base class for tools that produce Args
        pyrig.src.os.os.run_subprocess: Subprocess execution wrapper
    """

    __slots__ = ()

    def __str__(self) -> str:
        """Convert arguments to a space-separated string for display.

        Returns:
            Space-separated string of all arguments, suitable for display
            or logging. This is the command as it would appear in a shell.

        Example:
            >>> args = Args(("uv", "add", "requests"))
            >>> str(args)
            'uv add requests'
        """
        return " ".join(self)

    def run(self, *args: str, **kwargs: Any) -> CompletedProcess[Any]:
        """Execute the command represented by these arguments.

        Passes the arguments to `run_subprocess` for execution. All additional
        arguments and keyword arguments are forwarded to `run_subprocess`,
        allowing full control over subprocess behavior.

        Args:
            *args: Additional positional arguments to pass to run_subprocess.
                These are appended to the command arguments.
            **kwargs: Additional keyword arguments to pass to run_subprocess.
                Common options include:
                    - check (bool): Raise exception on non-zero exit
                    - capture_output (bool): Capture stdout/stderr
                    - cwd (Path): Working directory for the command

        Returns:
            The CompletedProcess object from subprocess execution, containing:
                - returncode: Exit code of the process
                - stdout: Standard output (if captured)
                - stderr: Standard error (if captured)

        Raises:
            subprocess.CalledProcessError: If check=True and the command fails.

        Example:
            Basic execution::

                >>> args = Args(("echo", "hello"))
                >>> result = args.run()
                >>> result.returncode
                0

            With error checking::

                >>> args = Args(("false",))  # Command that always fails
                >>> result = args.run(check=True)  # Raises CalledProcessError

            Capturing output::

                >>> args = Args(("echo", "hello"))
                >>> result = args.run(capture_output=True)
                >>> result.stdout.decode().strip()
                'hello'

        See Also:
            pyrig.src.os.os.run_subprocess: Subprocess execution implementation
        """
        return run_subprocess(self, *args, **kwargs)


class Tool(ABC):
    """Abstract base class for tool command argument construction.

    Provides a consistent interface for constructing command-line arguments
    for development tools. Subclasses implement the `name` method to specify
    the tool name, then use `get_args` to construct command arguments.

    The pattern enables type-safe, discoverable command construction:
        - Each tool method returns an `Args` object
        - Method names clearly indicate the command being constructed
        - Arguments are validated at construction time
        - Commands can be tested without execution

    Subclasses must implement:
        - `name`: Return the tool's command name (e.g., "git", "uv")

    Subclasses typically provide:
        - Multiple `get_*_args` methods for different commands
        - Clear documentation of what each method constructs

    Example:
        Implementing a tool wrapper::

            >>> class MyTool(Tool):
            ...     @classmethod
            ...     def name(cls) -> str:
            ...         return "mytool"
            ...
            ...     @classmethod
            ...     def get_build_args(cls, *args: str) -> Args:
            ...         return cls.get_args("build", *args)
            >>>
            >>> args = MyTool.get_build_args("--verbose")
            >>> print(args)
            mytool build --verbose

    See Also:
        Args: Command argument container
        pyrig.src.management.package_manager.PackageManager: UV tool wrapper
        pyrig.src.management.version_controller.VersionController: Git wrapper
    """

    @classmethod
    @abstractmethod
    def name(cls) -> str:
        """Get the command name of the tool.

        Returns:
            The tool's command name as it would be invoked in a shell
            (e.g., "git", "uv", "pytest", "pre-commit").

        Example:
            >>> class GitTool(Tool):
            ...     @classmethod
            ...     def name(cls) -> str:
            ...         return "git"
            >>> GitTool.name()
            'git'
        """

    @classmethod
    def get_args(cls, *args: str) -> Args:
        """Construct command arguments starting with the tool name.

        This is the base method used by all tool-specific argument construction
        methods. It prepends the tool name to the provided arguments.

        Args:
            *args: Command arguments to append after the tool name.

        Returns:
            Args object containing the tool name followed by the provided
            arguments.

        Example:
            >>> class GitTool(Tool):
            ...     @classmethod
            ...     def name(cls) -> str:
            ...         return "git"
            >>> args = GitTool.get_args("status", "--short")
            >>> print(args)
            git status --short

        Note:
            Subclasses typically don't call this directly. Instead, they
            provide higher-level methods that call `get_args` internally:

                @classmethod
                def get_status_args(cls) -> Args:
                    return cls.get_args("status", "--short")

        See Also:
            Args: Return type for this method
        """
        return Args((cls.name(), *args))
