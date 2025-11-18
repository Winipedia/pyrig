"""Tests for pyrig.os.os module."""

import pytest
from pytest_mock import MockFixture

from pyrig.src.os.os import run_subprocess, which_with_raise
from pyrig.src.testing.assertions import assert_with_msg


def test_which_with_raise(mocker: MockFixture) -> None:
    """Test func for which_with_raise."""
    # Test 1: Command found successfully
    expected_path = "/usr/bin/python"
    mock_which = mocker.patch("shutil.which", return_value=expected_path)

    result = which_with_raise("python")

    assert_with_msg(
        result == expected_path,
        f"Expected {expected_path}, got {result}",
    )
    mock_which.assert_called_with("python")

    # Test 2: Command not found
    mock_which.return_value = None

    with pytest.raises(FileNotFoundError, match="Command nonexistent_cmd not found"):
        which_with_raise("nonexistent_cmd")

    # Test 3: Empty command string
    with pytest.raises(FileNotFoundError, match="Command  not found"):
        which_with_raise("")

    # Test 4: Command with path separators
    expected_path_custom = "/usr/local/bin/custom-tool"
    mock_which.return_value = expected_path_custom

    result = which_with_raise("custom-tool")

    assert_with_msg(
        result == expected_path_custom,
        f"Expected {expected_path_custom}, got {result}",
    )


def test_run_subprocess() -> None:
    """Test func for run_subprocess."""
    cmd = ["echo", "hello"]
    res = run_subprocess(cmd)
    assert_with_msg(res.returncode == 0, "Expected returncode 0")
