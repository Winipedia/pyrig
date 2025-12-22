"""Pyrig command-line tool.

This module provides utilities for managing pyrig commands.
"""

from collections.abc import Callable
from typing import Any

from pyrig.src.management.base.base import Args, Tool
from pyrig.src.management.package_manager import PackageManager
from pyrig.src.modules.package import get_project_name_from_pkg_name


class Pyrigger(Tool):
    """Pyrig command-line tool.

    Provides methods for constructing pyrig command arguments and
    running pyrig commands through uv.
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
