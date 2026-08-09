"""module."""

from collections.abc import Callable, Iterable
from types import FunctionType

from pyrig.core.subprocesses import run_subprocess
from pyrig.rig.cli.commands.remove.pycache import remove_pycache
from pyrig.rig.cli.remove import pyc


def test_pyc(
    command_calls_function: Callable[[FunctionType, FunctionType, Iterable[str]], bool],
) -> None:
    """Test function."""
    assert command_calls_function(pyc, remove_pycache, [])
    result = run_subprocess(
        "pyrig",
        "rm",
        "pyc",
        "--help",
        check=False,
    )
    assert result.returncode == 0
