"""Pyrig CLI wrapper.

Provides type-safe wrapper for pyrig commands executed directly or through UV.
Used for programmatic execution of pyrig commands.

Example:
    >>> from pyrig.rig.tools.pyrigger import Pyrigger
    >>> from pyrig.rig.cli.subcommands import build
    >>> Pyrigger.I.cmd_args(cmd=build)  # pyrig build
"""

from collections.abc import Callable
from typing import Any

import pyrig
from pyrig.rig.tools.base.base import Tool, ToolGroup
from pyrig.src.modules.package import project_name_from_package_name
from pyrig.src.processes import Args


class Pyrigger(Tool):
    """Pyrig CLI wrapper.

    Constructs pyrig command arguments for programmatic execution.
    Commands constructed from function objects or string arguments.

    Operations:
        - Direct execution: Construct pyrig commands
        - Function-based: Convert function names to command names

    Example:
        >>> from pyrig.rig.cli.subcommands import build
        >>> Pyrigger.I.cmd_args(cmd=build).run()
    """

    @classmethod
    def name(cls) -> str:
        """Get tool name.

        Returns:
            'pyrig'
        """
        return pyrig.__name__

    @classmethod
    def group(cls) -> str:
        """Returns the group the tools belongs to.

        E.g. testing, tool, code-quality etc...
        """
        return ToolGroup.TOOLING

    @classmethod
    def badge_urls(cls) -> tuple[str, str]:
        """Returns the badge and connected page."""
        return (
            f"https://img.shields.io/badge/built%20with-{cls.name()}-3776AB?logo=buildkite&logoColor=black",
            f"https://github.com/Winipedia/{cls.name()}",
        )

    @classmethod
    def dev_dependencies(cls) -> list[str]:
        """Get tool dependencies.

        Returns:
            List of tool dependencies.
        """
        # only pyrig-dev not pyrig because pyrig is already installed as dependency
        return ["pyrig-dev"]

    @classmethod
    def cmd_args(cls, *args: str, cmd: Callable[..., Any]) -> Args:
        """Construct pyrig command arguments from callable.

        Args:
            *args: Command arguments passed after the command name.
            cmd: Callable whose name converts to command name (keyword-only).

        Returns:
            Args for 'pyrig <cmd_name>'.
        """
        cmd_name = project_name_from_package_name(cmd.__name__)  # ty:ignore[unresolved-attribute]
        return cls.args(cmd_name, *args)
