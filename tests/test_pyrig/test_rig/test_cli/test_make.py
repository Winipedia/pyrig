"""module."""

from collections.abc import Callable
from typing import Any

from pyrig.rig.cli.commands.make_fixture import make_fixture
from pyrig.rig.cli.commands.make_subclass import make_subclass
from pyrig.rig.cli.commands.make_subcommand import make_subcommand
from pyrig.rig.cli.make import cmd, fixture, subcls


def test_subcls(
    command_calls_function: Callable[[Callable[..., Any], Callable[..., Any]], None],
) -> None:
    """Test function."""
    command_calls_function(subcls, make_subclass)


def test_cmd(
    command_calls_function: Callable[[Callable[..., Any], Callable[..., Any]], None],
) -> None:
    """Test function."""
    command_calls_function(cmd, make_subcommand)


def test_fixture(
    command_calls_function: Callable[[Callable[..., Any], Callable[..., Any]], None],
) -> None:
    """Test function."""
    command_calls_function(fixture, make_fixture)
