"""module."""

from collections.abc import Callable
from typing import Any

from pyrig.rig.cli.commands.init_project import init_project
from pyrig.rig.cli.commands.remove_pycache import remove_pycache
from pyrig.rig.cli.commands.scratch import run_scratch_file
from pyrig.rig.cli.commands.synchronize import synchronize_project
from pyrig.rig.cli.subcommands import (
    init,
    rmpyc,
    scratch,
    sync,
)


def test_sync(
    command_works: Callable[[Callable[..., Any]], None],
    command_calls_function: Callable[[Callable[..., Any], Callable[..., Any]], None],
) -> None:
    """Test function."""
    command_works(sync)
    command_calls_function(sync, synchronize_project)


def test_init(
    command_works: Callable[[Callable[..., Any]], None],
    command_calls_function: Callable[[Callable[..., Any], Callable[..., Any]], None],
) -> None:
    """Test function."""
    command_works(init)
    command_calls_function(init, init_project)


def test_scratch(
    command_works: Callable[[Callable[..., Any]], None],
    command_calls_function: Callable[[Callable[..., Any], Callable[..., Any]], None],
) -> None:
    """Test function."""
    command_works(scratch)
    command_calls_function(scratch, run_scratch_file)


def test_rmpyc(
    command_works: Callable[[Callable[..., Any]], None],
    command_calls_function: Callable[[Callable[..., Any], Callable[..., Any]], None],
) -> None:
    """Test function."""
    command_works(rmpyc)
    command_calls_function(rmpyc, remove_pycache)
