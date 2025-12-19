"""Tests module."""

from pytest_mock import MockFixture

from pyrig.src.project.mgt import (
    Args,
    ContainerEngine,
    DependencyManager,
    PreCommit,
    Pyrig,
    TestRunner,
    VersionControl,
)


class TestArgs:
    """Test class."""

    def test___str__(self) -> None:
        """Test method."""
        args = Args(("uv", "run", "pytest"))
        result = str(args)
        assert result == "uv run pytest"

    def test_run(self, mocker: MockFixture) -> None:
        """Test method."""
        mock_run_subprocess = mocker.patch("pyrig.src.project.mgt.run_subprocess")
        args = Args(("uv", "--version"))
        args.run()
        mock_run_subprocess.assert_called_once_with(args)


class TestTool:
    """Test class."""

    def test_name(self) -> None:
        """Test method."""
        # Tool is abstract, test through concrete implementation
        assert DependencyManager.name() == "uv"

    def test_get_args(self) -> None:
        """Test method."""
        # Tool is abstract, test through concrete implementation
        result = DependencyManager.get_args("run", "pytest")
        assert result == ("uv", "run", "pytest")


class TestDependencyManager:
    """Test class."""

    def test_name(self) -> None:
        """Test method."""
        result = DependencyManager.name()
        assert result == "uv"

    def test_get_init_project_args(self) -> None:
        """Test method."""
        result = DependencyManager.get_init_project_args("--name", "myproject")
        assert result == ("uv", "init", "--name", "myproject")

    def test_get_run_args(self) -> None:
        """Test method."""
        result = DependencyManager.get_run_args("pytest")
        assert result == ("uv", "run", "pytest")

    def test_get_add_dependencies_args(self) -> None:
        """Test method."""
        result = DependencyManager.get_add_dependencies_args("pytest", "ruff")
        assert result == ("uv", "add", "pytest", "ruff")

    def test_get_add_dev_dependencies_args(self) -> None:
        """Test method."""
        result = DependencyManager.get_add_dev_dependencies_args("pytest", "ruff")
        assert result == ("uv", "add", "--group", "dev", "pytest", "ruff")

    def test_get_install_dependencies_args(self) -> None:
        """Test method."""
        result = DependencyManager.get_install_dependencies_args()
        assert result == ("uv", "sync")

    def test_get_update_dependencies_args(self) -> None:
        """Test method."""
        result = DependencyManager.get_update_dependencies_args()
        assert result == ("uv", "lock", "--upgrade")

    def test_get_update_self_args(self) -> None:
        """Test method."""
        result = DependencyManager.get_update_self_args()
        assert result == ("uv", "self", "update")

    def test_get_patch_version_args(self) -> None:
        """Test method."""
        result = DependencyManager.get_patch_version_args()
        assert result == ("uv", "version", "--bump", "patch")

    def test_get_build_args(self) -> None:
        """Test method."""
        result = DependencyManager.get_build_args()
        assert result == ("uv", "build")

    def test_get_publish_args(self) -> None:
        """Test method."""
        result = DependencyManager.get_publish_args("my-token")
        assert result == ("uv", "publish", "--token", "my-token")

    def test_get_version_args(self) -> None:
        """Test method."""
        result = DependencyManager.get_version_args()
        assert result == ("uv", "version")

    def test_get_version_short_args(self) -> None:
        """Test method."""
        result = DependencyManager.get_version_short_args()
        assert result == ("uv", "version", "--short")


class TestPyrig:
    """Test class."""

    def test_name(self) -> None:
        """Test method."""
        result = Pyrig.name()
        assert result == "pyrig"

    def test_get_cmd_args(self, mocker: MockFixture) -> None:
        """Test method."""
        # Mock the get_project_name_from_pkg_name function
        mocker.patch(
            "pyrig.src.project.mgt.get_project_name_from_pkg_name",
            return_value="my-command",
        )

        def my_command() -> None:
            """Sample command."""

        result = Pyrig.get_cmd_args(my_command, "--help")
        assert result == ("pyrig", "my-command", "--help")

    def test_get_venv_run_args(self) -> None:
        """Test method."""
        result = Pyrig.get_venv_run_args("--help")
        assert result == ("uv", "run", "pyrig", "--help")

    def test_get_venv_run_cmd_args(self, mocker: MockFixture) -> None:
        """Test method."""
        mocker.patch(
            "pyrig.src.project.mgt.get_project_name_from_pkg_name",
            return_value="my-command",
        )

        def my_command() -> None:
            """Sample command."""

        result = Pyrig.get_venv_run_cmd_args(my_command, "--verbose")
        assert result == ("uv", "run", "pyrig", "my-command", "--verbose")


class TestTestRunner:
    """Test class."""

    def test_name(self) -> None:
        """Test method."""
        result = TestRunner.name()
        assert result == "pytest"

    def test_get_run_tests_args(self) -> None:
        """Test method."""
        result = TestRunner.get_run_tests_args("-v")
        assert result == ("uv", "run", "pytest", "-v")

    def test_get_run_tests_in_ci_args(self) -> None:
        """Test method."""
        result = TestRunner.get_run_tests_in_ci_args()
        assert result == (
            "uv",
            "run",
            "pytest",
            "--log-cli-level=INFO",
            "--cov-report=xml",
        )


class TestVersionControl:
    """Test class."""

    def test_name(self) -> None:
        """Test method."""
        result = VersionControl.name()
        assert result == "git"

    def test_get_init_args(self) -> None:
        """Test method."""
        result = VersionControl.get_init_args()
        assert result == ("git", "init")

    def test_get_add_args(self) -> None:
        """Test method."""
        result = VersionControl.get_add_args("file.py")
        assert result == ("git", "add", "file.py")

    def test_get_add_all_args(self) -> None:
        """Test method."""
        result = VersionControl.get_add_all_args()
        assert result == ("git", "add", ".")

    def test_get_add_pyproject_toml_args(self) -> None:
        """Test method."""
        result = VersionControl.get_add_pyproject_toml_args()
        assert result == ("git", "add", "pyproject.toml")

    def test_get_add_pyproject_toml_and_uv_lock_args(self) -> None:
        """Test method."""
        result = VersionControl.get_add_pyproject_toml_and_uv_lock_args()
        assert result == ("git", "add", "pyproject.toml", "uv.lock")

    def test_get_commit_args(self) -> None:
        """Test method."""
        result = VersionControl.get_commit_args("-m", "Initial commit")
        assert result == ("git", "commit", "-m", "Initial commit")

    def test_get_commit_no_verify_args(self) -> None:
        """Test method."""
        result = VersionControl.get_commit_no_verify_args("Fix bug")
        assert result == ("git", "commit", "--no-verify", "-m", "Fix bug")

    def test_get_push_args(self) -> None:
        """Test method."""
        result = VersionControl.get_push_args()
        assert result == ("git", "push")

    def test_get_config_args(self) -> None:
        """Test method."""
        result = VersionControl.get_config_args("user.email", "test@example.com")
        assert result == ("git", "config", "user.email", "test@example.com")

    def test_get_config_global_args(self) -> None:
        """Test method."""
        result = VersionControl.get_config_global_args("user.email", "test@example.com")
        assert result == ("git", "config", "--global", "user.email", "test@example.com")

    def test_get_config_local_args(self) -> None:
        """Test method."""
        result = VersionControl.get_config_local_args("user.email", "test@example.com")
        assert result == ("git", "config", "--local", "user.email", "test@example.com")

    def test_get_config_local_user_email_args(self) -> None:
        """Test method."""
        result = VersionControl.get_config_local_user_email_args("test@example.com")
        assert result == ("git", "config", "--local", "user.email", "test@example.com")

    def test_get_config_local_user_name_args(self) -> None:
        """Test method."""
        result = VersionControl.get_config_local_user_name_args("Test User")
        assert result == ("git", "config", "--local", "user.name", "Test User")

    def test_get_config_global_user_email_args(self) -> None:
        """Test method."""
        result = VersionControl.get_config_global_user_email_args("test@example.com")
        assert result == ("git", "config", "--global", "user.email", "test@example.com")

    def test_get_config_global_user_name_args(self) -> None:
        """Test method."""
        result = VersionControl.get_config_global_user_name_args("Test User")
        assert result == ("git", "config", "--global", "user.name", "Test User")


class TestPreCommit:
    """Test class."""

    def test_name(self) -> None:
        """Test method."""
        result = PreCommit.name()
        assert result == "pre-commit"

    def test_get_install_args(self) -> None:
        """Test method."""
        result = PreCommit.get_install_args()
        assert result == ("pre-commit", "install")

    def test_get_run_args(self) -> None:
        """Test method."""
        result = PreCommit.get_run_args()
        assert result == ("pre-commit", "run")

    def test_get_run_all_files_args(self) -> None:
        """Test method."""
        result = PreCommit.get_run_all_files_args()
        assert result == ("pre-commit", "run", "--all-files")

    def test_get_run_all_files_verbose_args(self) -> None:
        """Test method."""
        result = PreCommit.get_run_all_files_verbose_args()
        assert result == ("pre-commit", "run", "--all-files", "--verbose")


class TestContainerEngine:
    """Test class."""

    def test_name(self) -> None:
        """Test method."""
        result = ContainerEngine.name()
        assert result == "podman"

    def test_get_build_args(self) -> None:
        """Test method."""
        result = ContainerEngine.get_build_args("-t", "myimage")
        assert result == ("podman", "build", "-t", "myimage")

    def test_get_save_args(self) -> None:
        """Test method."""
        result = ContainerEngine.get_save_args("-o", "image.tar")
        assert result == ("podman", "save", "-o", "image.tar")
