"""Pyrig CLI wrapper for executing pyrig commands programmatically.

This module provides a type-safe wrapper for pyrig command execution. The
`Pyrigger` class constructs pyrig command arguments that can be run through
UV's environment management or directly.

This is primarily used for programmatic execution of pyrig commands from within
pyrig itself or from dependent packages.

Example:
    >>> from pyrig.src.management.pyrigger import Pyrigger
    >>> from pyrig.dev.cli.subcommands import build
    >>>
    >>> # Construct command from function
    >>> build_args = Pyrigger.get_cmd_args(build)
    >>> print(build_args)
    pyrig build
    >>>
    >>> # Run through UV
    >>> venv_args = Pyrigger.get_venv_run_cmd_args(build)
    >>> print(venv_args)
    uv run pyrig build

See Also:
    pyrig.src.management.base.base.Tool: Base class for tool wrappers
    pyrig.src.management.package_manager.PackageManager: UV wrapper
    pyrig.dev.cli.subcommands: Pyrig CLI commands
"""

from collections.abc import Callable
from typing import Any

from pyrig.src.management.base.base import Args, Tool
from pyrig.src.management.package_manager import PackageManager
from pyrig.src.modules.package import get_project_name_from_pkg_name


class Pyrigger(Tool):
    """Pyrig CLI tool wrapper.

    Provides methods for constructing pyrig command arguments for programmatic
    execution. Commands can be constructed from function objects (using their
    names) or from string arguments.

    The class provides methods for:
        - **Direct execution**: Construct pyrig commands
        - **UV execution**: Construct uv run pyrig commands
        - **Function-based**: Convert function names to command names

    All methods return `Args` objects that can be executed via `.run()` or
    converted to strings for display.

    Example:
        >>> from pyrig.dev.cli.subcommands import build
        >>> # Direct command
        >>> Pyrigger.get_cmd_args(build).run()
        >>>
        >>> # Through UV
        >>> Pyrigger.get_venv_run_cmd_args(build).run()

    See Also:
        pyrig.src.management.base.base.Tool: Base class
        pyrig.src.modules.package.get_project_name_from_pkg_name: Name conversion
    """

    @classmethod
    def name(cls) -> str:
        """Get the tool name.

        Returns:
            str: The string 'pyrig'.
        """
        return "pyrig"

    @classmethod
    def get_cmd_args(cls, cmd: Callable[..., Any], *args: str) -> Args:
        """Construct pyrig command arguments from a callable.

        Args:
            cmd: Callable whose name will be converted to a command name.
            *args: Additional arguments to append to the command.

        Returns:
            Args: Command arguments for 'pyrig <cmd_name>'.
        """
        cmd_name = get_project_name_from_pkg_name(cmd.__name__)  # ty:ignore[unresolved-attribute]
        return cls.get_args(cmd_name, *args)

    @classmethod
    def get_venv_run_args(cls, *args: str) -> Args:
        """Construct uv run pyrig command arguments.

        Args:
            *args: Additional arguments to append to the pyrig command.

        Returns:
            Args: Command arguments for 'uv run pyrig'.
        """
        return PackageManager.get_run_args(*cls.get_args(*args))

    @classmethod
    def get_venv_run_cmd_args(cls, cmd: Callable[..., Any], *args: str) -> Args:
        """Construct uv run pyrig command arguments from a callable.

        Args:
            cmd: Callable whose name will be converted to a command name.
            *args: Additional arguments to append to the command.

        Returns:
            Args: Command arguments for 'uv run pyrig <cmd_name>'.
        """
        return PackageManager.get_run_args(*cls.get_cmd_args(cmd, *args))
