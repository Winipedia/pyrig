"""module."""

from collections.abc import Callable
from typing import Any

from pyrig_runtime.core.strings import snake_to_kebab_case

from pyrig.core.subprocesses import run_subprocess
from pyrig.rig.cli.commands.make.local import make_local_files
from pyrig.rig.cli.commands.make.subclass import make_subclass
from pyrig.rig.cli.commands.make.subcommand import make_subcommand
from pyrig.rig.cli.make import cmd, local, subcls


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


def test_subcls(
    command_calls_function: Callable[[Callable[..., Any], Callable[..., Any]], None],
) -> None:
    """Test function."""
    result = run_subprocess(
        ["pyrig", "mk", snake_to_kebab_case(subcls.__name__), "--help"], check=False
    )
    assert result.returncode == 0

    command_calls_function(subcls, make_subclass)
