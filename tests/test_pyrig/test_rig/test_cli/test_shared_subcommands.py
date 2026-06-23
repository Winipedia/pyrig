"""module."""

from collections.abc import Callable
from typing import Any

from pyrig.rig.cli.commands.version import project_version
from pyrig.rig.cli.shared_subcommands import version


def test_version(
    command_works: Callable[[Callable[..., Any]], None],
    command_calls_function: Callable[[Callable[..., Any], Callable[..., Any]], None],
) -> None:
    """Test function."""
    command_works(version)
    command_calls_function(version, project_version)
