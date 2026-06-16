"""module."""

from collections.abc import Callable
from typing import Any

from pyrig.rig.cli import subcommands
from pyrig.rig.cli.commands.init_project import init_project
from pyrig.rig.cli.commands.make_fixture import make_fixture
from pyrig.rig.cli.commands.make_subclass import make_subclass
from pyrig.rig.cli.commands.make_subcommand import make_subcommand
from pyrig.rig.cli.commands.protect_repo import protect_repository
from pyrig.rig.cli.commands.remove_pycache import remove_pycache
from pyrig.rig.cli.commands.scratch import run_scratch_file
from pyrig.rig.cli.commands.synchronize import synchronize_project
from pyrig.rig.cli.subcommands import (
    init,
    mkcmd,
    mkfixture,
    protect_repo,
    rmpyc,
    scratch,
    subcls,
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


def test_protect_repo(
    command_works: Callable[[Callable[..., Any]], None],
    command_calls_function: Callable[[Callable[..., Any], Callable[..., Any]], None],
) -> None:
    """Test function."""
    command_works(protect_repo)
    command_calls_function(protect_repo, protect_repository)


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


def test_mkcmd(
    command_works: Callable[[Callable[..., Any]], None],
    command_calls_function: Callable[[Callable[..., Any], Callable[..., Any]], None],
) -> None:
    """Test function."""
    command_works(mkcmd)
    command_calls_function(mkcmd, make_subcommand)


def test_subcls(
    command_works: Callable[[Callable[..., Any]], None],
    command_calls_function: Callable[[Callable[..., Any], Callable[..., Any]], None],
) -> None:
    """Test function."""
    command_works(subcls)
    command_calls_function(subcls, make_subclass)


def test_mkfixture(
    command_works: Callable[[Callable[..., Any]], None],
    command_calls_function: Callable[[Callable[..., Any], Callable[..., Any]], None],
) -> None:
    """Test function."""
    command_works(mkfixture)
    command_calls_function(mkfixture, make_fixture)


def test_module_docstring() -> None:
    """Test module docstring."""
    assert (
        subcommands.__doc__
        == """Project-specific CLI commands.

All functions in this module are automatically discovered and registered
as CLI commands for this project.
"""
    )
