"""Tests for pyrig.os.os module."""

import copy
import logging
import subprocess  # nosec: B404

import pytest
from pytest_mock import MockerFixture

from pyrig.core.subprocesses import Args, run_subprocess, run_subprocess_cached


def test_run_subprocess(caplog: pytest.LogCaptureFixture) -> None:
    """Test function."""
    with caplog.at_level(logging.ERROR, logger="pyrig.core.subprocesses"):
        cmd = ["echo", "hello"]
        res = run_subprocess(*cmd)
        assert res.returncode == 0, "Expected returncode 0"
        assert res.stdout == "hello\n", f"Expected stdout 'hello\n', got {res.stdout}"
        assert res.stderr == "", f"Expected stderr '', got {res.stderr}"
        assert not caplog.records, "Expected no log records on success"

        with pytest.raises(
            TypeError,
            match=r"shell",
        ):
            run_subprocess(*cmd, shell=True)  # ty: ignore[unknown-argument]  # noqa: S604  # nosec: B604
        assert not caplog.records, "Expected no log records on TypeError"

        fail_cmd = ["python", "-c", "import sys; sys.exit(1)"]
        with pytest.raises(subprocess.CalledProcessError):
            run_subprocess(*fail_cmd)

        assert len(caplog.records) == 1, "Expected exactly one log record on failure"
        record = caplog.records[0]
        assert record.name == "pyrig.core.subprocesses"
        assert record.levelname == "ERROR"
        assert record.exc_info is not None, "Expected exception info to be logged"
        assert record.getMessage() == (
            f"Subprocess command failed: {tuple(fail_cmd)}\n"
            "Return code: 1\n"
            "Stdout: \n"
            "Stderr: "
        ), "Expected formatted log message to include command, return code, and streams"


def test_run_subprocess_cached() -> None:
    """Test function."""
    result1 = run_subprocess_cached("echo", "hello")
    result2 = run_subprocess_cached("echo", "hello")
    assert result1 == result2, "Expected cached result to be the same"
    assert result1.returncode == 0, "Expected returncode 0"
    assert result1.stdout == "hello\n", (
        f"Expected stdout 'hello\n', got {result1.stdout}"
    )
    assert result1.stderr == "", f"Expected stderr '', got {result1.stderr}"


class TestArgs:
    """Test class."""

    def test___getnewargs__(self) -> None:
        """Test method."""
        args = Args("git", "commit", "-m", "msg")
        # tokens are returned unwrapped so Args(*tokens) rebuilds the instance
        assert args.__getnewargs__() == ("git", "commit", "-m", "msg")
        assert Args(*args.__getnewargs__()) == args

        # copy/deepcopy reconstruct through __getnewargs__: value and Args type
        # must both survive the round-trip
        for rebuilt in (copy.copy(args), copy.deepcopy(args)):
            assert rebuilt == args
            assert isinstance(rebuilt, Args)
            assert len(rebuilt) == len(args)

    def test___new__(self) -> None:
        """Test method."""
        args = Args("git", "commit", "-m", "msg")
        assert args == ("git", "commit", "-m", "msg")
        assert isinstance(args, Args)
        assert Args() == ()

    def test_run_cached(self) -> None:
        """Test method."""
        args = Args("echo", "hello")
        result1 = args.run_cached()
        result2 = args.run_cached()
        assert result1 == result2
        assert result1 is result2
        assert result1.returncode == 0, "Expected returncode 0"
        assert result1.stdout == "hello\n", (
            f"Expected stdout 'hello\n', got {result1.stdout}"
        )
        assert result1.stderr == "", f"Expected stderr '', got {result1.stderr}"

    def test___str__(self) -> None:
        """Test method."""
        args = Args("uv", "run", "pytest")
        result = str(args)
        assert result == "uv run pytest"

    def test_multiline(self) -> None:
        """Test method."""
        args = Args("uv", "run", "pytest")
        result = args.multiline()
        assert result == "uv \\\nrun \\\npytest"

    def test_run(self, mocker: MockerFixture) -> None:
        """Test method."""
        mock_run_subprocess = mocker.patch("subprocess.run")
        args = Args("uv", "--version")
        args.run()
        mock_run_subprocess.assert_called_once()
