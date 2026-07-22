"""module."""

from collections.abc import Callable, Iterable
from types import FunctionType

from pyrig_runtime.core.strings import snake_to_kebab_case

from pyrig.core.subprocesses import run_subprocess
from pyrig.rig.cli.commands.make.inits import make_project_init_files
from pyrig.rig.cli.commands.make.local import make_local_files
from pyrig.rig.cli.commands.make.subclass import make_subclass
from pyrig.rig.cli.commands.make.subcommand import make_subcommand
from pyrig.rig.cli.make import cmd, inits, local, subcls


def test_cmd(
    command_calls_function: Callable[[FunctionType, FunctionType, Iterable[str]], bool],
) -> None:
    """Test function."""
    assert command_calls_function(cmd, make_subcommand, ["my-command"])


def test_local(
    command_calls_function: Callable[[FunctionType, FunctionType, Iterable[str]], bool],
) -> None:
    """Test function."""
    assert command_calls_function(local, make_local_files, [])


def test_subcls(
    command_calls_function: Callable[[FunctionType, FunctionType, Iterable[str]], bool],
) -> None:
    """Test function."""
    result = run_subprocess(
        "pyrig",
        "mk",
        snake_to_kebab_case(subcls.__name__),
        "--help",
        check=False,
    )
    assert result.returncode == 0

    assert command_calls_function(subcls, make_subclass, [])


def test_inits(
    command_calls_function: Callable[[FunctionType, FunctionType, Iterable[str]], bool],
) -> None:
    """Test function."""
    assert command_calls_function(inits, make_project_init_files, [])
