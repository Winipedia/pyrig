"""module."""

from collections.abc import Callable
from contextlib import chdir
from pathlib import Path

import pytest

from pyrig.dev.configs.base.base import ConfigFile
from pyrig.dev.configs.git.gitignore import GitIgnoreConfigFile


@pytest.fixture
def my_test_gitignore_config_file(
    config_file_factory: Callable[[type[ConfigFile]], type[ConfigFile]],
) -> type[GitIgnoreConfigFile]:
    """Create a test gitignore config file class with tmp_path."""

    class MyTestGitIgnoreConfigFile(
        config_file_factory(GitIgnoreConfigFile)  # type: ignore [misc]
    ):
        """Test gitignore config file with tmp_path override."""

    return MyTestGitIgnoreConfigFile


class TestGitIgnoreConfigFile:
    """Test class."""

    def test_get_lines(
        self,
        my_test_gitignore_config_file: type[GitIgnoreConfigFile],
        tmp_path: Path,
    ) -> None:
        """Test method."""
        with chdir(tmp_path):
            my_test_gitignore_config_file.create_file()
            lines = my_test_gitignore_config_file.get_lines()
            assert "__pycache__/" in lines

    def test_get_github_python_gitignore_as_str(self) -> None:
        """Test method."""
        github_gitignore = GitIgnoreConfigFile.get_github_python_gitignore_as_str()
        assert "__pycache__/" in github_gitignore

    def test_get_github_python_gitignore_as_list(self) -> None:
        """Test method."""
        github_gitignore = GitIgnoreConfigFile.get_github_python_gitignore_as_list()
        assert "__pycache__/" in github_gitignore

    def test_get_filename(
        self, my_test_gitignore_config_file: type[GitIgnoreConfigFile]
    ) -> None:
        """Test method for get_filename."""
        filename = my_test_gitignore_config_file.get_filename()
        assert filename == "", f"Expected empty string, got {filename}"

    def test_get_parent_path(
        self,
        my_test_gitignore_config_file: type[GitIgnoreConfigFile],
        tmp_path: Path,
    ) -> None:
        """Test method for get_parent_path."""
        with chdir(tmp_path):
            parent_path = my_test_gitignore_config_file.get_parent_path()
            assert parent_path == Path(), f"Expected Path(), got {parent_path}"

    def test_get_file_extension(
        self, my_test_gitignore_config_file: type[GitIgnoreConfigFile]
    ) -> None:
        """Test method for get_file_extension."""
        extension = my_test_gitignore_config_file.get_file_extension()
        assert extension == "gitignore", f"Expected 'gitignore', got {extension}"
