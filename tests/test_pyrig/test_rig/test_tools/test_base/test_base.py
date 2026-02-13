"""Tests module."""

from pyrig.rig import tools
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.tools.base.base import Tool
from pyrig.rig.tools.package_manager import PackageManager


class TestTool:
    """Test class."""

    def test_definition_package(self) -> None:
        """Test method."""
        result = Tool.definition_package()
        assert result == tools

    def test_sorting_key(self) -> None:
        """Test method."""
        result = Tool.sorting_key(PackageManager.I)
        assert isinstance(result, str)

    def test_group(self) -> None:
        """Test method."""
        result = PackageManager.I.group()
        assert isinstance(result, str)
        assert result == "tooling"

    def test_badge_urls(self) -> None:
        """Test method."""
        result = PackageManager.I.badge_urls()
        assert isinstance(result, tuple)

        assert all(isinstance(url, str) for url in result)

    def test_badge(self) -> None:
        """Test method."""
        result = PackageManager.I.badge()
        assert isinstance(result, str)
        assert "uv" in result
        assert "[![" in result

    def test_grouped_badges(self) -> None:
        """Test method."""
        result = Tool.grouped_badges()
        assert isinstance(result, dict)
        assert len(result) > 0
        assert all(
            isinstance(k, str) and isinstance(v, list) for k, v in result.items()
        )

    def test_dev_dependencies(self) -> None:
        """Test method."""
        result = PackageManager.I.dev_dependencies()
        assert result == []

    def test_subclasses_dev_dependencies(self) -> None:
        """Test method."""
        result = Tool.subclasses_dev_dependencies()
        # should be the same as the dev dependencies in pyproject.toml
        no_version_from_toml = [
            PyprojectConfigFile.remove_version_from_dep(dep)
            for dep in PyprojectConfigFile.dev_dependencies()
        ]
        assert result == no_version_from_toml

    def test_name(self) -> None:
        """Test method."""
        # Tool is abstract, test through concrete implementation
        assert PackageManager.I.name() == "uv"

    def test_args(self) -> None:
        """Test method."""
        # Tool is abstract, test through concrete implementation
        result = PackageManager.I.args("run", "pytest")
        assert result == ("uv", "run", "pytest")


class TestToolGroup:
    """Test class."""
