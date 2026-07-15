"""module."""

from pathlib import Path

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.version_control.hooks.manager import VersionControlHookManager


class TestPackageManager:
    """Test class."""

    def test_add_group_args(self) -> None:
        """Test method."""
        assert PackageManager.I.add_group_args("smth") == (
            "uv",
            "add",
            "--group",
            "smth",
        )

    def test_add_args(self) -> None:
        """Test method."""
        assert PackageManager.I.add_args("smth") == ("uv", "add", "smth")

    def test_install_dependencies_no_dev_args(self) -> None:
        """Test method."""
        assert PackageManager.I.install_dependencies_no_dev_args("hello") == (
            "uv",
            "sync",
            "--no-group",
            "dev",
            "hello",
        )

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            PackageManager.I.image_url()
            == "https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert PackageManager.I.link_url() == "https://github.com/astral-sh/uv"

    def test_version_control_ignore_patterns(self) -> None:
        """Test method."""
        assert PackageManager.I.version_control_ignore_patterns() == (".venv", "dist/")

    def test_lock_file(self) -> None:
        """Test method."""
        assert PackageManager.I.lock_file() == Path("uv.lock")

    def test_source_root(self) -> None:
        """Test method."""
        assert PackageManager.I.source_root() == Path("src")

    def test_package_root(self) -> None:
        """Test method."""
        assert PackageManager.I.package_root() == Path("src/pyrig")

    def test_project_cmd_args(self) -> None:
        """Test method."""

        def test_project_cmd_args(arg: str) -> tuple[str, str, str]:
            return ("pyrig", "test-project-cmd-args", arg)

        result = PackageManager.I.project_cmd_args("arg", cmd=test_project_cmd_args)
        assert result == Args("pyrig", "test-project-cmd-args", "arg")

    def test_project_name(self) -> None:
        """Test method."""
        result = PackageManager.I.project_name()
        assert result == "pyrig"

    def test_package_name(self) -> None:
        """Test method."""
        result = PackageManager.I.package_name()
        assert result == "pyrig"

    def test_group(self) -> None:
        """Test method."""
        result = PackageManager.I.group()
        assert isinstance(result, str)
        assert result == "tooling"

    def test_dev_dependencies(self) -> None:
        """Test method."""
        result = PackageManager.I.dev_dependencies()
        assert result == ()

    def test_build_system_requires(self) -> None:
        """Test method."""
        result = PackageManager.I.build_system_requires()
        assert result == ["uv_build"]

    def test_build_backend(self) -> None:
        """Test method."""
        result = PackageManager.I.build_backend()
        assert result == "uv_build"

    def test_no_auto_install_env_var(self) -> None:
        """Test method."""
        result = PackageManager.I.no_auto_install_env_var()
        assert result == "UV_NO_SYNC"

    def test_name(self) -> None:
        """Test method."""
        result = PackageManager.I.name()
        assert result == "uv"

    def test_run_args(self) -> None:
        """Test method."""
        result = PackageManager.I.run_args("pytest")
        assert result == ("uv", "run", "pytest")

    def test_add_dev_dependencies_args(self) -> None:
        """Test method."""
        result = PackageManager.I.add_dev_dependencies_args("pytest", "ruff")
        assert result == ("uv", "add", "--group", "dev", "pytest", "ruff")

    def test_install_dependencies_args(self) -> None:
        """Test method."""
        result = PackageManager.I.install_dependencies_args()
        assert result == ("uv", "sync")

    def test_update_dependencies_args(self) -> None:
        """Test method."""
        result = PackageManager.I.update_dependencies_args()
        assert result == ("uv", "lock", "--upgrade")

    def test_version_args(self) -> None:
        """Test method."""
        result = PackageManager.I.version_args()
        assert result == ("uv", "version")

    def test_version_short_args(self) -> None:
        """Test method."""
        result = PackageManager.I.version_short_args()
        assert result == ("uv", "version", "--short")

    def test_build_args(self) -> None:
        """Test method."""
        result = PackageManager.I.build_args()
        assert result == ("uv", "build")

    def test_version_control_hooks(self) -> None:
        """Test method."""
        assert PackageManager.I.version_control_hooks() == (
            PackageManager.I.update_dependencies_hook(),
            PackageManager.I.install_dependencies_hook(),
        )

    def test_update_dependencies_hook(self) -> None:
        """Test method."""
        hook = PackageManager.I.update_dependencies_hook()
        assert hook["priority"] == 0
        assert hook["stages"] == VersionControlHookManager.I.transition_stages()
        assert hook["always_run"] is True
        assert hook["pass_filenames"] is False

    def test_update_dependencies(self) -> None:
        """Test method."""
        assert (
            PackageManager.I.update_dependencies()
            == PackageManager.I.update_dependencies_args()
        )

    def test_install_dependencies_hook(self) -> None:
        """Test method."""
        # installing depends on the lock file update having already run
        update_hook = PackageManager.I.update_dependencies_hook()
        install_hook = PackageManager.I.install_dependencies_hook()
        assert install_hook["priority"] > update_hook["priority"]
        assert install_hook["stages"] == VersionControlHookManager.I.transition_stages()

    def test_install_dependencies(self) -> None:
        """Test method."""
        assert (
            PackageManager.I.install_dependencies()
            == PackageManager.I.install_dependencies_args()
        )
