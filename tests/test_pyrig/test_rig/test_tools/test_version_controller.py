"""module."""

from pathlib import Path

from pyrig.rig.tools.version_controller import VersionController


class TestVersionController:
    """Test class."""

    def test_ignore_filename(self) -> None:
        """Test method."""
        result = VersionController.L.ignore_filename()
        assert result == ".gitignore", f"Expected '.gitignore', got {result}"

    def test_group(self) -> None:
        """Test method."""
        result = VersionController.L.group()
        assert isinstance(result, str)
        assert result == "tooling"

    def test_badge_urls(self) -> None:
        """Test method."""
        result = VersionController.L.badge_urls()
        assert isinstance(result, tuple)
        assert all(isinstance(url, str) for url in result)

    def test_dev_dependencies(self) -> None:
        """Test method."""
        result = VersionController.L.dev_dependencies()
        assert result == []

    def test_config_get_user_email_args(self) -> None:
        """Test method."""
        result = VersionController.L.config_get_user_email_args()
        assert result == ("git", "config", "--get", "user.email")

    def test_email(self) -> None:
        """Test method."""
        result = VersionController.L.email()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_default_branch(self) -> None:
        """Test method."""
        result = VersionController.L.default_branch()
        assert result == "main"

    def test_default_ruleset_name(self) -> None:
        """Test method."""
        result = VersionController.L.default_ruleset_name()
        assert result == "main-protection"

    def test_diff_quiet_args(self) -> None:
        """Test method."""
        result = VersionController.L.diff_quiet_args()
        assert result == ("git", "diff", "--quiet")

    def test_config_get_args(self) -> None:
        """Test method."""
        result = VersionController.L.config_get_args()
        assert result == ("git", "config", "--get")

    def test_config_remote_origin_url_args(self) -> None:
        """Test method."""
        result = VersionController.L.config_remote_origin_url_args()
        assert result == ("git", "config", "--get", "remote.origin.url")

    def test_config_get_user_name_args(self) -> None:
        """Test method."""
        result = VersionController.L.config_get_user_name_args()
        assert result == ("git", "config", "--get", "user.name")

    def test_diff_args(self) -> None:
        """Test method."""
        result = VersionController.L.diff_args()
        assert result == ("git", "diff")

    def test_push_origin_args(self) -> None:
        """Test method."""
        result = VersionController.L.push_origin_args()
        assert result == ("git", "push", "origin")

    def test_push_origin_tag_args(self) -> None:
        """Test method."""
        tag = "v1.2.3"
        result = VersionController.L.push_origin_tag_args(tag=tag)
        assert result == ("git", "push", "origin", tag)

    def test_tag_args(self) -> None:
        """Test method."""
        tag = "v1.2.3"
        result = VersionController.L.tag_args(tag=tag)
        assert result == ("git", "tag", tag)

    def test_name(self) -> None:
        """Test method."""
        result = VersionController.L.name()
        assert result == "git"

    def test_init_args(self) -> None:
        """Test method."""
        result = VersionController.L.init_args()
        assert result == ("git", "init")

    def test_add_args(self) -> None:
        """Test method."""
        result = VersionController.L.add_args("file.py")
        assert result == ("git", "add", "file.py")

    def test_add_all_args(self) -> None:
        """Test method."""
        result = VersionController.L.add_all_args()
        assert result == ("git", "add", ".")

    def test_add_pyproject_toml_args(self) -> None:
        """Test method."""
        result = VersionController.L.add_pyproject_toml_args()
        assert result == ("git", "add", "pyproject.toml")

    def test_add_pyproject_toml_and_lock_file_args(self) -> None:
        """Test method."""
        result = VersionController.L.add_pyproject_toml_and_lock_file_args()
        assert result == ("git", "add", "pyproject.toml", "uv.lock")

    def test_commit_args(self) -> None:
        """Test method."""
        result = VersionController.L.commit_args("-m", "Initial commit")
        assert result == ("git", "commit", "-m", "Initial commit")

    def test_commit_no_verify_args(self) -> None:
        """Test method."""
        result = VersionController.L.commit_no_verify_args(msg="Fix bug")
        assert result == ("git", "commit", "--no-verify", "-m", "Fix bug")

    def test_push_args(self) -> None:
        """Test method."""
        result = VersionController.L.push_args()
        assert result == ("git", "push")

    def test_config_args(self) -> None:
        """Test method."""
        result = VersionController.L.config_args("user.email", "test@example.com")
        assert result == ("git", "config", "user.email", "test@example.com")

    def test_config_global_args(self) -> None:
        """Test method."""
        result = VersionController.L.config_global_args(
            "user.email", "test@example.com"
        )
        assert result == ("git", "config", "--global", "user.email", "test@example.com")

    def test_config_local_args(self) -> None:
        """Test method."""
        result = VersionController.L.config_local_args("user.email", "test@example.com")
        assert result == ("git", "config", "--local", "user.email", "test@example.com")

    def test_config_local_user_email_args(self) -> None:
        """Test method."""
        result = VersionController.L.config_local_user_email_args(
            email="test@example.com"
        )
        assert result == ("git", "config", "--local", "user.email", "test@example.com")

    def test_config_local_user_name_args(self) -> None:
        """Test method."""
        result = VersionController.L.config_local_user_name_args(name="Test User")
        assert result == ("git", "config", "--local", "user.name", "Test User")

    def test_config_global_user_email_args(self) -> None:
        """Test method."""
        result = VersionController.L.config_global_user_email_args(
            email="test@example.com"
        )
        assert result == ("git", "config", "--global", "user.email", "test@example.com")

    def test_config_global_user_name_args(self) -> None:
        """Test method."""
        result = VersionController.L.config_global_user_name_args(name="Test User")
        assert result == ("git", "config", "--global", "user.name", "Test User")

    def test_ignore_path(self) -> None:
        """Test method."""
        result = VersionController.L.ignore_path()
        assert result == Path(".gitignore")

    def test_loaded_ignore(self) -> None:
        """Test method."""
        result = VersionController.L.loaded_ignore()
        assert isinstance(result, list)
        assert all(isinstance(item, str) for item in result)

    def test_repo_owner_and_name(self) -> None:
        """Test method."""
        result = VersionController.L.repo_owner_and_name()
        assert isinstance(result, tuple)
        assert all(isinstance(item, str) for item in result)

    def test_repo_remote(self) -> None:
        """Test method."""
        result = VersionController.L.repo_remote()
        assert isinstance(result, str)

    def test_username(self) -> None:
        """Test method."""
        result = VersionController.L.username()
        assert isinstance(result, str)

    def test_diff(self) -> None:
        """Test method."""
        result = VersionController.L.diff()
        assert isinstance(result, str)

    def test_has_unstaged_diff(self) -> None:
        """Test method."""
        result = VersionController.L.has_unstaged_diff()
        assert isinstance(result, bool)
