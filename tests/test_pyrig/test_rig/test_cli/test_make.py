"""module."""

from collections.abc import Callable
from typing import Any

from pyrig.rig.cli.commands.make.subcommand import make_subcommand
from pyrig.rig.cli.make import cmd


def test_cmd(
    command_calls_function: Callable[[Callable[..., Any], Callable[..., Any]], None],
) -> None:
    """Test function."""
    command_calls_function(cmd, make_subcommand)
