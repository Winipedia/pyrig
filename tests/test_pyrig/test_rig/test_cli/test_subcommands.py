"""module."""

from collections.abc import Callable, Iterable
from types import FunctionType

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
    command_works: Callable[[FunctionType], bool],
    command_calls_function: Callable[[FunctionType, FunctionType, Iterable[str]], bool],
) -> None:
    """Test function."""
    assert command_works(sync)
    assert command_calls_function(sync, synchronize_project, [])


def test_init(
    command_works: Callable[[FunctionType], bool],
    command_calls_function: Callable[[FunctionType, FunctionType, Iterable[str]], bool],
) -> None:
    """Test function."""
    assert command_works(init)
    assert command_calls_function(init, init_project, [])


def test_scratch(
    command_works: Callable[[FunctionType], bool],
    command_calls_function: Callable[[FunctionType, FunctionType, Iterable[str]], bool],
) -> None:
    """Test function."""
    assert command_works(scratch)
    assert command_calls_function(scratch, run_scratch_file, [])


def test_rmpyc(
    command_works: Callable[[FunctionType], bool],
    command_calls_function: Callable[[FunctionType, FunctionType, Iterable[str]], bool],
) -> None:
    """Test function."""
    assert command_works(rmpyc)
    assert command_calls_function(rmpyc, remove_pycache, [])
