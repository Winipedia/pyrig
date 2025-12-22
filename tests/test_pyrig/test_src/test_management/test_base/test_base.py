"""Tests module."""

from pytest_mock import MockFixture

from pyrig.src.management.base.base import (
    Args,
)
from pyrig.src.management.package_manager import PackageManager


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


class TestTool:
    """Test class."""

    def test_name(self) -> None:
        """Test method."""
        # Tool is abstract, test through concrete implementation
        assert PackageManager.name() == "uv"

    def test_get_args(self) -> None:
        """Test method."""
        # Tool is abstract, test through concrete implementation
        result = PackageManager.get_args("run", "pytest")
        assert result == ("uv", "run", "pytest")
