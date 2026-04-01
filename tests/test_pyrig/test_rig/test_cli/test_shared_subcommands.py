"""module."""

from collections.abc import Callable
from typing import Any

from pyrig.rig.cli.shared_subcommands import version


def test_version(command_works: Callable[[Callable[..., Any]], None]) -> None:
    """Test function."""
    command_works(version)
