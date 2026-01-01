"""Tests for pyrig.os.os module."""

from pytest_mock import MockFixture

from pyrig.src.processes import Args, run_subprocess


def test_run_subprocess() -> None:
    """Test func for run_subprocess."""
    cmd = ["echo", "hello"]
    res = run_subprocess(cmd)
    assert res.returncode == 0, "Expected returncode 0"


class TestArgs:
    """Test class."""

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
