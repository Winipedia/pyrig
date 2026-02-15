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

    def name(self) -> str:
        """Get tool name.

        Returns:
            'pyrig'
        """
        return pyrig.__name__

    def group(self) -> str:
        """Returns the group the tool belongs to.

        Returns:
            `ToolGroup.TOOLING`
        """
        return ToolGroup.TOOLING

    def badge_urls(self) -> tuple[str, str]:
        """Get pyrig badge image URL and GitHub page URL.

        Returns:
            Tuple of badge image URL and GitHub page URL.
        """
        return (
            f"https://img.shields.io/badge/built%20with-{self.name()}-3776AB?logo=buildkite&logoColor=black",
            f"https://github.com/Winipedia/{self.name()}",
        )

    def dev_dependencies(self) -> list[str]:
        """Get tool dependencies.

        Returns:
            List of tool dependencies.
        """
        # only pyrig-dev not pyrig because pyrig is already installed as dependency
        return ["pyrig-dev"]

    def cmd_args(self, *args: str, cmd: Callable[..., Any]) -> Args:
        """Construct pyrig command arguments from callable.

        Args:
            *args: Command arguments passed after the command name.
            cmd: Callable whose name converts to command name (keyword-only).

        Returns:
            Args for 'pyrig <cmd_name>'.
        """
        cmd_name = project_name_from_package_name(cmd.__name__)  # type: ignore[attr-defined]
        return self.args(cmd_name, *args)
