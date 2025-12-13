"""Tests module."""

import pyrig
from pyrig.src.project.mgt import (
    get_pyrig_cli_cmd_args,
    get_pyrig_cli_cmd_script,
    get_script_from_args,
)
from pyrig.src.testing.assertions import assert_with_msg


def test_get_script_from_args() -> None:
    """Test func for get_script_from_args."""
    # Test with simple args
    result = get_script_from_args(["smth1", "smth2", "smth3"])
    assert result == "smth1 smth2 smth3"

    # Test with single arg
    result = get_script_from_args(["python"])
    assert_with_msg(
        result == "python",
        f"Expected 'python', got '{result}'",
    )

    # Test with empty args
    result = get_script_from_args([])
    assert_with_msg(
        result == "",
        f"Expected empty string, got '{result}'",
    )


def test_get_pyrig_cli_cmd_args() -> None:
    """Test function."""
    args = get_pyrig_cli_cmd_args(get_pyrig_cli_cmd_args)
    expected = [pyrig.__name__, get_pyrig_cli_cmd_args.__name__.replace("_", "-")]

    assert args == expected


def test_get_pyrig_cli_cmd_script() -> None:
    """Test function."""
    args = get_pyrig_cli_cmd_script(get_pyrig_cli_cmd_args)
    expected = f"{pyrig.__name__} {get_pyrig_cli_cmd_args.__name__.replace('_', '-')}"

    assert args == expected
