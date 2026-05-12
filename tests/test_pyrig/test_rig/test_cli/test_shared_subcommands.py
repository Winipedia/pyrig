"""module."""

from collections.abc import Callable
from typing import Any

from pyrig.rig.cli import shared_subcommands
from pyrig.rig.cli.commands.version import project_version
from pyrig.rig.cli.shared_subcommands import version


def test_version(
    command_works: Callable[[Callable[..., Any]], None],
    command_calls_function: Callable[[Callable[..., Any], Callable[..., Any]], None],
) -> None:
    """Test function."""
    command_works(version)
    command_calls_function(version, project_version)


def test_module_docstring() -> None:
    """Test module docstring."""
    assert (
        shared_subcommands.__doc__
        == """Shared CLI commands available across all dependent projects.

Every function defined here is automatically discovered and registered
as a CLI command in all installed pyrig based projects.
"""
    )
