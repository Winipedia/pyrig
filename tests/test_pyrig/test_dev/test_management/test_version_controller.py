"""module."""

from pathlib import Path

from pyrig.dev.management.version_controller import VersionController


class TestVersionController:
    """Test class."""

    def test_get_config_get_args(self) -> None:
        """Test method."""
        result = VersionController.L.get_config_get_args()
        assert result == ("git", "config", "--get")

    def test_get_config_get_remote_origin_url_args(self) -> None:
        """Test method."""
        result = VersionController.L.get_config_get_remote_origin_url_args()
        assert result == ("git", "config", "--get", "remote.origin.url")

    def test_get_config_get_user_name_args(self) -> None:
        """Test method."""
        result = VersionController.L.get_config_get_user_name_args()
        assert result == ("git", "config", "--get", "user.name")

    def test_get_diff_args(self) -> None:
        """Test method."""
        result = VersionController.L.get_diff_args()
        assert result == ("git", "diff")

    def test_get_push_origin_args(self) -> None:
        """Test method."""
        result = VersionController.L.get_push_origin_args()
        assert result == ("git", "push", "origin")

    def test_get_push_origin_tag_args(self) -> None:
        """Test method."""
        tag = "v1.2.3"
        result = VersionController.L.get_push_origin_tag_args(tag=tag)
        assert result == ("git", "push", "origin", tag)

    def test_get_tag_args(self) -> None:
        """Test method."""
        tag = "v1.2.3"
        result = VersionController.L.get_tag_args(tag=tag)
        assert result == ("git", "tag", tag)

    def test_name(self) -> None:
        """Test method."""
        result = VersionController.L.name()
        assert result == "git"

    def test_get_init_args(self) -> None:
        """Test method."""
        result = VersionController.L.get_init_args()
        assert result == ("git", "init")

    def test_get_add_args(self) -> None:
        """Test method."""
        result = VersionController.L.get_add_args("file.py")
        assert result == ("git", "add", "file.py")

    def test_get_add_all_args(self) -> None:
        """Test method."""
        result = VersionController.L.get_add_all_args()
        assert result == ("git", "add", ".")

    def test_get_add_pyproject_toml_args(self) -> None:
        """Test method."""
        result = VersionController.L.get_add_pyproject_toml_args()
        assert result == ("git", "add", "pyproject.toml")

    def test_get_add_pyproject_toml_and_lock_file_args(self) -> None:
        """Test method."""
        result = VersionController.L.get_add_pyproject_toml_and_lock_file_args()
        assert result == ("git", "add", "pyproject.toml", "uv.lock")

    def test_get_commit_args(self) -> None:
        """Test method."""
        result = VersionController.L.get_commit_args("-m", "Initial commit")
        assert result == ("git", "commit", "-m", "Initial commit")

    def test_get_commit_no_verify_args(self) -> None:
        """Test method."""
        result = VersionController.L.get_commit_no_verify_args(msg="Fix bug")
        assert result == ("git", "commit", "--no-verify", "-m", "Fix bug")

    def test_get_push_args(self) -> None:
        """Test method."""
        result = VersionController.L.get_push_args()
        assert result == ("git", "push")

    def test_get_config_args(self) -> None:
        """Test method."""
        result = VersionController.L.get_config_args("user.email", "test@example.com")
        assert result == ("git", "config", "user.email", "test@example.com")

    def test_get_config_global_args(self) -> None:
        """Test method."""
        result = VersionController.L.get_config_global_args(
            "user.email", "test@example.com"
        )
        assert result == ("git", "config", "--global", "user.email", "test@example.com")

    def test_get_config_local_args(self) -> None:
        """Test method."""
        result = VersionController.L.get_config_local_args(
            "user.email", "test@example.com"
        )
        assert result == ("git", "config", "--local", "user.email", "test@example.com")

    def test_get_config_local_user_email_args(self) -> None:
        """Test method."""
        result = VersionController.L.get_config_local_user_email_args(
            email="test@example.com"
        )
        assert result == ("git", "config", "--local", "user.email", "test@example.com")

    def test_get_config_local_user_name_args(self) -> None:
        """Test method."""
        result = VersionController.L.get_config_local_user_name_args(name="Test User")
        assert result == ("git", "config", "--local", "user.name", "Test User")

    def test_get_config_global_user_email_args(self) -> None:
        """Test method."""
        result = VersionController.L.get_config_global_user_email_args(
            email="test@example.com"
        )
        assert result == ("git", "config", "--global", "user.email", "test@example.com")

    def test_get_config_global_user_name_args(self) -> None:
        """Test method."""
        result = VersionController.L.get_config_global_user_name_args(name="Test User")
        assert result == ("git", "config", "--global", "user.name", "Test User")

    def test_get_ignore_path(self) -> None:
        """Test method."""
        result = VersionController.L.get_ignore_path()
        assert result == Path(".gitignore")

    def test_get_loaded_ignore(self) -> None:
        """Test method."""
        result = VersionController.L.get_loaded_ignore()
        assert isinstance(result, list)
        assert all(isinstance(item, str) for item in result)

    def test_get_repo_owner_and_name(self) -> None:
        """Test method."""
        result = VersionController.L.get_repo_owner_and_name()
        assert isinstance(result, tuple)
        assert all(isinstance(item, str) for item in result)

    def test_get_repo_remote(self) -> None:
        """Test method."""
        result = VersionController.L.get_repo_remote()
        assert isinstance(result, str)

    def test_get_username(self) -> None:
        """Test method."""
        result = VersionController.L.get_username()
        assert isinstance(result, str)

    def test_get_diff(self) -> None:
        """Test method."""
        result = VersionController.L.get_diff()
        assert isinstance(result, str)
