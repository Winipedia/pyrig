"""Tests module."""

from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.tools.base.base import Tool
from pyrig.rig.tools.package_manager import PackageManager


class TestTool:
    """Test class."""

    def test_get_dev_dependencies(self) -> None:
        """Test method."""
        result = PackageManager.L.get_dev_dependencies()
        assert result == []

    def test_get_all_tool_dev_deps(self) -> None:
        """Test method."""
        result = Tool.get_all_tool_dev_deps()
        # should be the same as the dev dependencies in pyproject.toml
        no_version_from_toml = [
            PyprojectConfigFile.remove_version_from_dep(dep)
            for dep in PyprojectConfigFile.get_dev_dependencies()
        ]
        assert result == no_version_from_toml

    def test_L(self) -> None:  # noqa: N802
        """Test method."""
        assert PackageManager.L.L is PackageManager

    def test_name(self) -> None:
        """Test method."""
        # Tool is abstract, test through concrete implementation
        assert PackageManager.L.name() == "uv"

    def test_get_args(self) -> None:
        """Test method."""
        # Tool is abstract, test through concrete implementation
        result = PackageManager.L.get_args("run", "pytest")
        assert result == ("uv", "run", "pytest")
