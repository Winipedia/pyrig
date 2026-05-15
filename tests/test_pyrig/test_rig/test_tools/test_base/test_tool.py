"""Tests module."""

from pyrig.rig import tools
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.tools.base.tool import Tool
from pyrig.rig.tools.package_manager import PackageManager


class TestTool:
    """Test class."""

    def test_version_control_ignore_paths(self) -> None:
        """Test method."""
        assert PackageManager.I.version_control_ignore_paths() == (".venv", "dist/")

    def test_subclasses_version_control_ignore_paths(self) -> None:
        """Test method."""
        ignore_paths = Tool.subclasses_version_control_ignore_paths()
        for path in (".venv", "dist/", ".coverage", ".pytest_cache/"):
            assert path in ignore_paths

    def test___str__(self) -> None:
        """Test method."""
        assert "uv" in str(PackageManager.I)

    def test_dependency_package(self) -> None:
        """Test method."""
        result = Tool.dependency_package()
        assert result == tools

    def test_sort_key(self) -> None:
        """Test method."""
        result = PackageManager.sort_key()
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
        assert result == ()

    def test_subclasses_dev_dependencies(self) -> None:
        """Test method."""
        deps = Tool.subclasses_dev_dependencies()
        toml_deps = PyprojectConfigFile.I.dev_dependencies()
        toml_deps_no_versions = tuple(dep.split(">=")[0] for dep in toml_deps)

        assert set(deps) == set(toml_deps_no_versions)

    def test_name(self) -> None:
        """Test method."""
        # Tool is abstract, test through concrete implementation
        assert PackageManager.I.name() == "uv"

    def test_args(self) -> None:
        """Test method."""
        # Tool is abstract, test through concrete implementation
        result = PackageManager.I.args("run", "pytest")
        assert result == ("uv", "run", "pytest")
