"""Shared pytest fixtures for testing the project's CLI commands.

Provides helpers that assert a CLI command is registered and reachable, and
that a command delegates to its expected implementation function.
"""

from collections.abc import Callable
from typing import Any

import pytest
from pytest_mock import MockerFixture

from pyrig.rig.tools.package_manager import PackageManager


@pytest.fixture
def command_works() -> Callable[[Callable[..., Any]], None]:
    """Return a callable that verifies a CLI command is registered and executable.

    The returned function runs the command with ``--help`` and asserts that
    the command executes successfully and that its name appears in stdout.

    Returns:
        A callable ``(cmd) -> None`` that accepts a CLI function and asserts
        it is reachable and produces help output.
    """

    def check(cmd: Callable[..., Any]) -> None:
        # run the --help command to see if it is available
        args = PackageManager.I.project_cmd_args("--help", cmd=cmd)
        completed_process = args.run()
        stdout = completed_process.stdout
        name = cmd.__name__.replace("_", "-")  # ty:ignore[unresolved-attribute]
        assert name in stdout

    return check


@pytest.fixture
def command_calls_function(
    mocker: MockerFixture,
) -> Callable[[Callable[..., Any], Callable[..., Any]], None]:
    """Return a callable that verifies a CLI command delegates to the expected function.

    The returned function patches the target function by its fully qualified
    name, invokes the command, and asserts the patch was called exactly once.

    Args:
        mocker: pytest-mock fixture for patching.

    Returns:
        A callable ``(cmd, function) -> None`` that asserts ``cmd`` calls
        ``function`` exactly once.
    """

    def check(cmd: Callable[..., Any], function: Callable[..., Any]) -> None:
        mock = mocker.patch(function.__module__ + "." + function.__name__)  # ty:ignore[unresolved-attribute]
        cmd()
        mock.assert_called_once()

    return check
