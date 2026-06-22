"""module."""

from collections.abc import Callable
from typing import Any

from pyrig.rig.cli.commands.make.local import make_local_files
from pyrig.rig.cli.commands.make.subcommand import make_subcommand
from pyrig.rig.cli.make import cmd, local


def test_cmd(
    command_calls_function: Callable[[Callable[..., Any], Callable[..., Any]], None],
) -> None:
    """Test function."""
    command_calls_function(cmd, make_subcommand)


def test_local(
    command_calls_function: Callable[[Callable[..., Any], Callable[..., Any]], None],
) -> None:
    """Test function."""
    command_calls_function(local, make_local_files)
