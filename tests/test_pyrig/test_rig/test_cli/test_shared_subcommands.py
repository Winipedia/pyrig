"""module."""

from collections.abc import Callable
from typing import Any

import pytest

from pyrig.rig.cli.shared_subcommands import version


def test_version(
    command_works: Callable[[Callable[..., Any]], None],
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test function."""
    command_works(version)

    assert version() is None

    captured = capsys.readouterr()
    out, err = captured.out, captured.err
    assert out.startswith("pytest version ")
    assert err == ""
