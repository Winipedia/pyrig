"""module."""

from pyrig.rig.tools.package_manager import PackageManager


class TestPackageManager:
    """Test class."""

    def test_group(self) -> None:
        """Test method."""
        result = PackageManager.L.group()
        assert isinstance(result, str)
        assert result == "tooling"

    def test_badge_urls(self) -> None:
        """Test method."""
        result = PackageManager.L.badge_urls()
        assert isinstance(result, tuple)
        assert all(isinstance(url, str) for url in result)

    def test_dev_dependencies(self) -> None:
        """Test method."""
        result = PackageManager.L.dev_dependencies()
        assert result == []

    def test_build_system_requires(self) -> None:
        """Test method."""
        result = PackageManager.L.build_system_requires()
        assert result == ["uv_build"]

    def test_build_backend(self) -> None:
        """Test method."""
        result = PackageManager.L.build_backend()
        assert result == "uv_build"

    def test_get_no_auto_install_env_var(self) -> None:
        """Test method."""
        result = PackageManager.L.get_no_auto_install_env_var()
        assert result == "UV_NO_SYNC"

    def test_run_no_dev_args(self) -> None:
        """Test method."""
        result = PackageManager.L.run_no_dev_args("pytest")
        assert result == ("uv", "run", "--no-group", "dev", "pytest")

    def test_install_dependencies_no_dev_args(self) -> None:
        """Test method."""
        result = PackageManager.L.install_dependencies_args("--no-group", "dev")
        assert result == ("uv", "sync", "--no-group", "dev")

    def test_name(self) -> None:
        """Test method."""
        result = PackageManager.L.name()
        assert result == "uv"

    def test_get_init_project_args(self) -> None:
        """Test method."""
        result = PackageManager.L.get_init_project_args("--name", "myproject")
        assert result == ("uv", "init", "--name", "myproject")

    def test_run_args(self) -> None:
        """Test method."""
        result = PackageManager.L.run_args("pytest")
        assert result == ("uv", "run", "pytest")

    def test_add_dependencies_args(self) -> None:
        """Test method."""
        result = PackageManager.L.add_dependencies_args("pytest", "ruff")
        assert result == ("uv", "add", "pytest", "ruff")

    def test_add_dev_dependencies_args(self) -> None:
        """Test method."""
        result = PackageManager.L.add_dev_dependencies_args("pytest", "ruff")
        assert result == ("uv", "add", "--group", "dev", "pytest", "ruff")

    def test_install_dependencies_args(self) -> None:
        """Test method."""
        result = PackageManager.L.install_dependencies_args()
        assert result == ("uv", "sync")

    def test_update_dependencies_args(self) -> None:
        """Test method."""
        result = PackageManager.L.update_dependencies_args()
        assert result == ("uv", "lock", "--upgrade")

    def test_update_self_args(self) -> None:
        """Test method."""
        result = PackageManager.L.update_self_args()
        assert result == ("uv", "self", "update")

    def test_get_patch_version_args(self) -> None:
        """Test method."""
        result = PackageManager.L.get_patch_version_args()
        assert result == ("uv", "version", "--bump", "patch")

    def test_build_args(self) -> None:
        """Test method."""
        result = PackageManager.L.build_args()
        assert result == ("uv", "build")

    def test_get_publish_args(self) -> None:
        """Test method."""
        result = PackageManager.L.get_publish_args(token="my-token")  # noqa: S106  # nosec B106
        assert result == ("uv", "publish", "--token", "my-token")

    def test_version_args(self) -> None:
        """Test method."""
        result = PackageManager.L.version_args()
        assert result == ("uv", "version")

    def test_version_short_args(self) -> None:
        """Test method."""
        result = PackageManager.L.version_short_args()
        assert result == ("uv", "version", "--short")
