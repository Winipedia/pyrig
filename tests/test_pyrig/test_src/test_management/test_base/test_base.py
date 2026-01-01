"""Tests module."""

from pyrig.src.management.package_manager import PackageManager


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
