"""Tests for pyrig.os.os module."""

from pytest_mock import MockFixture

from pyrig.src.processes import Args, run_subprocess, run_subprocess_cached


def test_run_subprocess() -> None:
    """Test function."""
    cmd = ["echo", "hello"]
    res = run_subprocess(cmd)
    assert res.returncode == 0, "Expected returncode 0"
    assert res.stdout == "hello\n", f"Expected stdout 'hello\n', got {res.stdout}"
    assert res.stderr == "", f"Expected stderr '', got {res.stderr}"


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

    def test___repr__(self) -> None:
        """Test method."""
        args = Args(("uv", "run", "pytest"))
        result = repr(args)
        assert result == "uv run pytest"
        assert repr(args) == str(args)

    def test___str__(self) -> None:
        """Test method."""
        args = Args(("uv", "run", "pytest"))
        result = str(args)
        assert result == "uv run pytest"

    def test_run(self, mocker: MockFixture) -> None:
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
