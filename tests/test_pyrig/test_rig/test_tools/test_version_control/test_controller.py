"""module."""

from contextlib import chdir
from pathlib import Path

from pytest_mock import MockerFixture

from pyrig.core.subprocesses import Args, run_subprocess_cached
from pyrig.rig.tools.version_control.controller import VersionController


class TestVersionController:
    """Test class."""

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            VersionController.I.image_url()
            == "https://img.shields.io/badge/Git-F05032?logo=git&logoColor=white"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert VersionController.I.link_url() == "https://git-scm.com"

    def test_remote_repo_owner(self, mocker: MockerFixture) -> None:
        """Test method."""
        assert VersionController.I.remote_repo_owner() == "Winipedia"

        # make sure empty string return passes through as empty string
        mock_remote_url = mocker.patch.object(
            VersionController,
            VersionController.remote_url.__name__,
            return_value="",
        )
        assert VersionController.I.remote_repo_owner() == ""
        mock_remote_url.assert_called_once()

    def test_commit_with_msg_args(self) -> None:
        """Test method."""
        result = VersionController.I.commit_with_msg_args(msg="Initial commit")
        assert result == ("git", "commit", "--message=Initial commit")

    def test_resolve_repo_owner(self, mocker: MockerFixture) -> None:
        """Test method."""
        result = VersionController().resolve_repo_owner()
        assert result == "Winipedia"

        # mock remote_url to return empty string
        remote_mock = mocker.patch.object(
            VersionController,
            VersionController.remote_url.__name__,
            return_value="",
        )
        username_mock = mocker.patch.object(
            VersionController,
            VersionController.username.__name__,
            return_value="Test User",
        )
        result = VersionController().resolve_repo_owner()
        owner = result
        assert owner == "TestUser"
        username_mock.assert_called_once()
        remote_mock.assert_called_once()

        username_mock.return_value = "TestUser"
        result = VersionController().resolve_repo_owner()
        assert result == "TestUser"

        # make it return a https remote url
        remote_mock.return_value = "https://github.com/OWNER/REPO.git"
        result = VersionController().resolve_repo_owner()
        assert result == "OWNER"

        # make it return a ssh remote url
        remote_mock.return_value = "git@github.com:OWNER/REPO.git"
        result = VersionController().resolve_repo_owner()
        assert result == "OWNER"

    def test_group(self) -> None:
        """Test method."""
        result = VersionController.I.group()
        assert isinstance(result, str)
        assert result == "tooling"

    def test_dev_dependencies(self) -> None:
        """Test method."""
        result = VersionController.I.dev_dependencies()
        assert result == ()

    def test_config_get_user_email_args(self) -> None:
        """Test method."""
        result = VersionController.I.config_get_user_email_args()
        assert result == ("git", "config", "--get", "user.email")

    def test_email(self, mocker: MockerFixture) -> None:
        """Test method."""
        run_mock = mocker.patch.object(
            Args,
            Args.run_cached.__name__,
            return_value=mocker.Mock(stdout="some.email@here.com\n"),
        )
        result = VersionController.I.email()
        run_mock.assert_called_once()
        assert result == "some.email@here.com"

    def test_default_branch(self) -> None:
        """Test method."""
        result = VersionController.I.default_branch()
        assert result == "main"

    def test_config_get_args(self) -> None:
        """Test method."""
        result = VersionController.I.config_get_args()
        assert result == ("git", "config", "--get")

    def test_config_remote_origin_url_args(self) -> None:
        """Test method."""
        result = VersionController.I.config_remote_origin_url_args()
        assert result == ("git", "config", "--get", "remote.origin.url")

    def test_config_get_username_args(self) -> None:
        """Test method."""
        result = VersionController.I.config_get_username_args()
        assert result == ("git", "config", "--get", "user.name")

    def test_push_origin_args(self) -> None:
        """Test method."""
        result = VersionController.I.push_origin_args()
        assert result == ("git", "push", "origin")

    def test_push_origin_tag_args(self) -> None:
        """Test method."""
        tag = "v1.2.3"
        result = VersionController.I.push_origin_tag_args(tag=tag)
        assert result == ("git", "push", "origin", tag)

    def test_tag_args(self) -> None:
        """Test method."""
        tag = "v1.2.3"
        result = VersionController.I.tag_args(tag=tag)
        assert result == ("git", "tag", tag)

    def test_name(self) -> None:
        """Test method."""
        result = VersionController.I.name()
        assert result == "git"

    def test_init_args(self) -> None:
        """Test method."""
        result = VersionController.I.init_args()
        assert result == ("git", "init")

    def test_add_args(self) -> None:
        """Test method."""
        result = VersionController.I.add_args("file.py")
        assert result == ("git", "add", "file.py")

    def test_add_all_args(self) -> None:
        """Test method."""
        result = VersionController.I.add_all_args()
        assert result == ("git", "add", ".")

    def test_commit_args(self) -> None:
        """Test method."""
        result = VersionController.I.commit_args("-m", "Initial commit")
        assert result == ("git", "commit", "-m", "Initial commit")

    def test_push_args(self) -> None:
        """Test method."""
        result = VersionController.I.push_args()
        assert result == ("git", "push")

    def test_config_args(self) -> None:
        """Test method."""
        result = VersionController.I.config_args("user.email", "test@example.com")
        assert result == ("git", "config", "user.email", "test@example.com")

    def test_repo_owner(self) -> None:
        """Test method."""
        result = VersionController.I.repo_owner()
        assert isinstance(result, str)

    def test_remote_url(self, tmp_path: Path) -> None:
        """Test method."""
        assert "github" in VersionController.I.remote_url()

        # make sure no remote given gets us empty string
        with chdir(tmp_path):
            run_subprocess_cached.cache_clear()
            result = VersionController.I.remote_url()
            run_subprocess_cached.cache_clear()
            assert result == ""

        assert "github" in VersionController.I.remote_url()

    def test_username(self, mocker: MockerFixture) -> None:
        """Test method."""
        run_mock = mocker.patch.object(
            Args,
            Args.run_cached.__name__,
            return_value=mocker.Mock(stdout="Some User\n"),
        )
        result = VersionController.I.username()
        run_mock.assert_called_once()
        assert result == "Some User"

    def test_normalized_username(self, mocker: MockerFixture) -> None:
        """Test method."""
        mock_run = mocker.patch.object(
            Args,
            Args.run_cached.__name__,
            return_value=mocker.Mock(stdout="Winipedia\n"),
        )

        result = VersionController.I.normalized_username()
        mock_run.assert_called_once()
        assert result == "Winipedia"

        mock_run.return_value = mocker.Mock(stdout="Some User\n")
        result = VersionController.I.normalized_username()
        mock_run.call_count = 2
        assert result == "SomeUser"
