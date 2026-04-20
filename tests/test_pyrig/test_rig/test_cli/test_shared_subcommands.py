"""module."""

from collections.abc import Callable
from typing import Any

import pytest
from pytest_mock import MockerFixture

from pyrig.core.cli import project_name_from_argv
from pyrig.rig.cli import shared_subcommands
from pyrig.rig.cli.shared_subcommands import version


def test_version(
    command_works: Callable[[Callable[..., Any]], None],
    capsys: pytest.CaptureFixture[str],
    mocker: MockerFixture,
) -> None:
    """Test function."""
    command_works(version)

    # mock project_name_from_argv to return "pyrig"
    mocker.patch(
        shared_subcommands.__name__ + "." + project_name_from_argv.__name__,
        return_value="pyrig",
    )

    assert version() is None

    captured = capsys.readouterr()
    out, err = captured.out, captured.err
    assert out.startswith("pyrig version ")
    assert err == ""
