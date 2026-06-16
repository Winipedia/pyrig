"""test module."""

from collections.abc import Callable
from typing import Any

from pyrig.rig.cli.commands.make_root import make_project_root
from pyrig.rig.cli.shared_subcommands import version
from pyrig.rig.cli.subcommands import mkroot


def test_command_works(command_works: Callable[[Callable[..., Any]], None]) -> None:
    """Test function."""
    command_works(version)


def test_command_calls_function(
    command_calls_function: Callable[[Callable[..., Any], Callable[..., Any]], None],
) -> None:
    """Test function."""
    command_calls_function(mkroot, make_project_root)
