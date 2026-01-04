"""Pyrig CLI wrapper.

Provides type-safe wrapper for pyrig commands executed directly or through UV.
Used for programmatic execution of pyrig commands.

Example:
    >>> from pyrig.dev.management.pyrigger import Pyrigger
    >>> from pyrig.dev.cli.subcommands import build
    >>> Pyrigger.L.get_cmd_args(cmd=build)  # pyrig build
"""

from collections.abc import Callable
from typing import Any

from pyrig.dev.management.base.base import Tool
from pyrig.src.modules.package import get_project_name_from_pkg_name
from pyrig.src.processes import Args


class Pyrigger(Tool):
    """Pyrig CLI wrapper.

    Constructs pyrig command arguments for programmatic execution.
    Commands constructed from function objects or string arguments.

    Operations:
        - Direct execution: Construct pyrig commands
        - Function-based: Convert function names to command names

    Example:
        >>> from pyrig.dev.cli.subcommands import build
        >>> Pyrigger.L.get_cmd_args(cmd=build).run()
    """

    @classmethod
    def name(cls) -> str:
        """Get tool name.

        Returns:
            'pyrig'
        """
        return "pyrig"

    @classmethod
    def get_cmd_args(cls, *args: str, cmd: Callable[..., Any]) -> Args:
        """Construct pyrig command arguments from callable.

        Args:
            *args: Command arguments passed after the command name.
            cmd: Callable whose name converts to command name (keyword-only).

        Returns:
            Args for 'pyrig <cmd_name>'.
        """
        cmd_name = get_project_name_from_pkg_name(cmd.__name__)  # ty:ignore[unresolved-attribute]
        return cls.get_args(cmd_name, *args)
