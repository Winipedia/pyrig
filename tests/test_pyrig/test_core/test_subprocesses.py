"""Tests for pyrig.os.os module."""

import logging
from subprocess import CalledProcessError  # nosec: B404

import pytest
from pytest_mock import MockerFixture

from pyrig.core.subprocesses import Args, run_subprocess, run_subprocess_cached


def test_run_subprocess(
    mocker: MockerFixture, caplog: pytest.LogCaptureFixture
) -> None:
    """Test function."""
    cmd = ["echo", "hello"]
    res = run_subprocess(cmd)
    assert res.returncode == 0, "Expected returncode 0"
    assert res.stdout == "hello\n", f"Expected stdout 'hello\n', got {res.stdout}"
    assert res.stderr == "", f"Expected stderr '', got {res.stderr}"

    with pytest.raises(RuntimeError, match="Shell mode is forbidden"):
        run_subprocess(cmd, shell=True)  # noqa: S604  # nosec: B604

    # mock run to raise CalledProcessError
    mock_run = mocker.patch("subprocess.run", side_effect=CalledProcessError(1, cmd))
    with caplog.at_level(logging.ERROR), pytest.raises(CalledProcessError):
        run_subprocess(cmd)
    mock_run.assert_called_once()
    # Check that the error was logged
    assert any(
        "Command failed: ['echo', 'hello'] (exit code 1)" in record.message
        for record in caplog.records
    )


class TestArgs:
    """Test class."""

    def test_run_cached(self) -> None:
        """Test method."""
        args = Args(("echo", "hello"))
        result1 = args.run_cached()
        result2 = args.run_cached()
        assert result1 == result2, "Expected cached result to be the same"
        assert result1.returncode == 0, "Expected returncode 0"
        assert result1.stdout == "hello\n", (
            f"Expected stdout 'hello\n', got {result1.stdout}"
        )
        assert result1.stderr == "", f"Expected stderr '', got {result1.stderr}"

    def test___str__(self) -> None:
        """Test method."""
        args = Args(("uv", "run", "pytest"))
        result = str(args)
        assert result == "uv run pytest"

    def test_run(self, mocker: MockerFixture) -> None:
        """Test method."""
        mock_run_subprocess = mocker.patch("subprocess.run")
        args = Args(("uv", "--version"))
        args.run()
        mock_run_subprocess.assert_called_once()


def test_run_subprocess_cached() -> None:
    """Test function."""
    result1 = run_subprocess_cached(("echo", "hello"))
    result2 = run_subprocess_cached(("echo", "hello"))
    assert result1 == result2, "Expected cached result to be the same"
    assert result1.returncode == 0, "Expected returncode 0"
    assert result1.stdout == "hello\n", (
        f"Expected stdout 'hello\n', got {result1.stdout}"
    )
    assert result1.stderr == "", f"Expected stderr '', got {result1.stderr}"
