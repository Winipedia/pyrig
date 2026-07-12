"""Tests module."""

from pytest_mock import MockerFixture

from pyrig.rig import tools
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.tools.base.tool import Group, Tool
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.project_tester import ProjectTester


class TestTool:
    """Test class."""

    def test_config_name(self, mocker: MockerFixture) -> None:
        """Test method."""
        assert PackageManager.I.config_name() == "uv"
        assert ProjectTester.I.config_name() == "pytest"

        mock = mocker.patch.object(
            PackageManager,
            PackageManager.name.__name__,
            return_value="my-tool",
        )
        assert PackageManager.I.config_name() == "my_tool"
        mock.assert_called_once()

    def test_groups(self) -> None:
        """Test method."""
        all_groups = [v for k, v in vars(Group).items() if k.isupper()]
        groups = Tool.groups()
        assert set(groups) == set(all_groups)
        assert len(groups) > 1

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            PackageManager.I.image_url()
            == "https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert PackageManager.I.link_url() == "https://github.com/astral-sh/uv"

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

    def test_discovery_module(self) -> None:
        """Test method."""
        result = Tool.discovery_module()
        assert result == tools

    def test_group(self) -> None:
        """Test method."""
        result = PackageManager.I.group()
        assert isinstance(result, str)
        assert result == "tooling"

    def test_badge(self) -> None:
        """Test method."""
        result = PackageManager.I.badge()
        assert isinstance(result, str)
        assert "uv" in result
        assert "[![" in result

    def test_grouped_badges(self) -> None:
        """Test method."""
        badges1 = Tool.grouped_badges()
        assert isinstance(badges1, dict)
        assert len(badges1) > 0
        assert all(
            isinstance(k, str) and isinstance(v, list) for k, v in badges1.items()
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

        assert set(deps).issubset(set(toml_deps_no_versions))

    def test_name(self) -> None:
        """Test method."""
        # Tool is abstract, test through concrete implementation
        assert PackageManager.I.name() == "uv"

    def test_args(self) -> None:
        """Test method."""
        # Tool is abstract, test through concrete implementation
        result = PackageManager.I.args("run", "pytest")
        assert result == ("uv", "run", "pytest")
