"""module."""

from pyrig.rig.tools.package_manager import PackageManager


class TestPackageManager:
    """Test class."""

    def test_get_group(self) -> None:
        """Test method."""
        result = PackageManager.L.get_group()
        assert isinstance(result, str)
        assert result == "tooling"

    def test_get_badge_urls(self) -> None:
        """Test method."""
        result = PackageManager.L.get_badge_urls()
        assert isinstance(result, tuple)
        assert all(isinstance(url, str) for url in result)

    def test_get_dev_dependencies(self) -> None:
        """Test method."""
        result = PackageManager.L.get_dev_dependencies()
        assert result == []

    def test_get_build_system_requires(self) -> None:
        """Test method."""
        result = PackageManager.L.get_build_system_requires()
        assert result == ["uv_build"]

    def test_get_build_backend(self) -> None:
        """Test method."""
        result = PackageManager.L.get_build_backend()
        assert result == "uv_build"

    def test_get_no_auto_install_env_var(self) -> None:
        """Test method."""
        result = PackageManager.L.get_no_auto_install_env_var()
        assert result == "UV_NO_SYNC"

    def test_get_run_no_dev_args(self) -> None:
        """Test method."""
        result = PackageManager.L.get_run_no_dev_args("pytest")
        assert result == ("uv", "run", "--no-group", "dev", "pytest")

    def test_get_install_dependencies_no_dev_args(self) -> None:
        """Test method."""
        result = PackageManager.L.get_install_dependencies_args("--no-group", "dev")
        assert result == ("uv", "sync", "--no-group", "dev")

    def test_name(self) -> None:
        """Test method."""
        result = PackageManager.L.name()
        assert result == "uv"

    def test_get_init_project_args(self) -> None:
        """Test method."""
        result = PackageManager.L.get_init_project_args("--name", "myproject")
        assert result == ("uv", "init", "--name", "myproject")

    def test_get_run_args(self) -> None:
        """Test method."""
        result = PackageManager.L.get_run_args("pytest")
        assert result == ("uv", "run", "pytest")

    def test_get_add_dependencies_args(self) -> None:
        """Test method."""
        result = PackageManager.L.get_add_dependencies_args("pytest", "ruff")
        assert result == ("uv", "add", "pytest", "ruff")

    def test_get_add_dev_dependencies_args(self) -> None:
        """Test method."""
        result = PackageManager.L.get_add_dev_dependencies_args("pytest", "ruff")
        assert result == ("uv", "add", "--group", "dev", "pytest", "ruff")

    def test_get_install_dependencies_args(self) -> None:
        """Test method."""
        result = PackageManager.L.get_install_dependencies_args()
        assert result == ("uv", "sync")

    def test_get_update_dependencies_args(self) -> None:
        """Test method."""
        result = PackageManager.L.get_update_dependencies_args()
        assert result == ("uv", "lock", "--upgrade")

    def test_get_update_self_args(self) -> None:
        """Test method."""
        result = PackageManager.L.get_update_self_args()
        assert result == ("uv", "self", "update")

    def test_get_patch_version_args(self) -> None:
        """Test method."""
        result = PackageManager.L.get_patch_version_args()
        assert result == ("uv", "version", "--bump", "patch")

    def test_get_build_args(self) -> None:
        """Test method."""
        result = PackageManager.L.get_build_args()
        assert result == ("uv", "build")

    def test_get_publish_args(self) -> None:
        """Test method."""
        result = PackageManager.L.get_publish_args(token="my-token")  # noqa: S106  # nosec B106
        assert result == ("uv", "publish", "--token", "my-token")

    def test_get_version_args(self) -> None:
        """Test method."""
        result = PackageManager.L.get_version_args()
        assert result == ("uv", "version")

    def test_get_version_short_args(self) -> None:
        """Test method."""
        result = PackageManager.L.get_version_short_args()
        assert result == ("uv", "version", "--short")
