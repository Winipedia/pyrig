"""module."""

from collections.abc import Callable
from pathlib import Path

import pytest
from pytest_mock import MockFixture

from py_dev.dev.configs import pre_commit
from py_dev.dev.configs.base.base import YamlConfigFile
from py_dev.dev.configs.pre_commit import PreCommitConfigConfigFile
from py_dev.utils.modules.module import make_obj_importpath
from py_dev.utils.testing.assertions import assert_with_msg


@pytest.fixture
def my_test_pre_commit_config_file(
    config_file_factory: Callable[[type[YamlConfigFile]], type[YamlConfigFile]],
) -> type[PreCommitConfigConfigFile]:
    """Create a test pre-commit config file class with tmp_path."""

    class MyTestPreCommitConfigFile(
        config_file_factory(PreCommitConfigConfigFile)  # type: ignore [misc]
    ):
        """Test pre-commit config file with tmp_path override."""

    return MyTestPreCommitConfigFile


class TestPreCommitConfigConfigFile:
    """Test class for PreCommitConfigConfigFile."""

    def test_get_hook(self) -> None:
        """Test method for get_hook."""
        hook = PreCommitConfigConfigFile.get_hook("test", ["test"])
        assert_with_msg(
            hook["id"] == "test",
            f"Expected id to be 'test', got {hook['id']}",
        )

    def test_run_hooks(self, mocker: MockFixture) -> None:
        """Test method for run_hooks."""
        mock_run = mocker.patch(make_obj_importpath(pre_commit) + ".run_subprocess")
        PreCommitConfigConfigFile.run_hooks()
        mock_run.assert_called()

    def test_get_filename(
        self, my_test_pre_commit_config_file: type[PreCommitConfigConfigFile]
    ) -> None:
        """Test method for get_filename."""
        filename = my_test_pre_commit_config_file.get_filename()
        # Filename starts with . and contains pre-commit
        assert_with_msg(
            filename.startswith("."),
            f"Expected filename to start with '.', got {filename}",
        )
        assert_with_msg(
            "pre-commit" in filename,
            f"Expected 'pre-commit' in filename, got {filename}",
        )

    def test_get_parent_path(
        self, my_test_pre_commit_config_file: type[PreCommitConfigConfigFile]
    ) -> None:
        """Test method for get_parent_path."""
        parent_path = my_test_pre_commit_config_file.get_parent_path()
        assert_with_msg(
            parent_path == Path(),
            f"Expected Path(), got {parent_path}",
        )

    def test_get_configs(
        self, my_test_pre_commit_config_file: type[PreCommitConfigConfigFile]
    ) -> None:
        """Test method for get_configs."""
        configs = my_test_pre_commit_config_file.get_configs()
        assert_with_msg(
            "repos" in configs,
            "Expected 'repos' key in configs",
        )
        assert_with_msg(
            isinstance(configs["repos"], list),
            "Expected 'repos' to be a list",
        )
        assert_with_msg(
            len(configs["repos"]) > 0,
            "Expected at least one repo in configs",
        )
        repo = configs["repos"][0]
        assert_with_msg(
            repo["repo"] == "local",
            f"Expected repo to be 'local', got {repo['repo']}",
        )
        assert_with_msg(
            "hooks" in repo,
            "Expected 'hooks' key in repo",
        )
        assert_with_msg(
            isinstance(repo["hooks"], list),
            "Expected 'hooks' to be a list",
        )
        assert_with_msg(
            len(repo["hooks"]) > 0,
            "Expected at least one hook in repo",
        )

    def test___init__(
        self,
        my_test_pre_commit_config_file: type[PreCommitConfigConfigFile],
        mocker: MockFixture,
    ) -> None:
        """Test method for __init__."""
        # Mock install to avoid running pre-commit install
        mocker.patch.object(
            my_test_pre_commit_config_file,
            "install",
        )
        # Create instance
        my_test_pre_commit_config_file()
        # Verify instance was created successfully

    def test_install(
        self,
        my_test_pre_commit_config_file: type[PreCommitConfigConfigFile],
        mocker: MockFixture,
    ) -> None:
        """Test method for install."""
        # Mock run_subprocess to avoid actually running pre-commit install
        mock_run = mocker.patch(make_obj_importpath(pre_commit) + ".run_subprocess")
        my_test_pre_commit_config_file.install()
        mock_run.assert_called_once()
