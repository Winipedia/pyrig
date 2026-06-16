"""test module."""

from collections.abc import Callable
from typing import Any

from pyrig.rig.cli.commands.make_subclass import make_subclass
from pyrig.rig.cli.shared_subcommands import version
from pyrig.rig.cli.subcommands import subcls


def test_command_works(command_works: Callable[[Callable[..., Any]], None]) -> None:
    """Test function."""
    command_works(version)


def test_command_calls_function(
    command_calls_function: Callable[[Callable[..., Any], Callable[..., Any]], None],
) -> None:
    """Test function."""
    command_calls_function(subcls, make_subclass)
