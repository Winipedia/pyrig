"""Pyrig CLI wrapper.

Provides type-safe wrapper for pyrig commands executed directly or through UV.
Used for programmatic execution of pyrig commands.

Example:
    >>> from pyrig.src.management.pyrigger import Pyrigger
    >>> from pyrig.dev.cli.subcommands import build
    >>> Pyrigger.L.get_cmd_args(build)  # pyrig build
    >>> Pyrigger.L.get_venv_run_cmd_args(build)  # uv run pyrig build
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
        - UV execution: Construct uv run pyrig commands
        - Function-based: Convert function names to command names

    Example:
        >>> from pyrig.dev.cli.subcommands import build
        >>> Pyrigger.L.get_cmd_args(build).run()
        >>> Pyrigger.L.get_venv_run_cmd_args(build).run()
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
            cmd: Callable whose name converts to command name.
            *args: Command arguments.

        Returns:
            Args for 'pyrig <cmd_name>'.
        """
        cmd_name = get_project_name_from_pkg_name(cmd.__name__)  # ty:ignore[unresolved-attribute]
        return cls.get_args(cmd_name, *args)
