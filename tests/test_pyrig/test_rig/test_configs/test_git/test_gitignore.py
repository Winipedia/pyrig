"""module."""

from collections.abc import Callable
from contextlib import chdir
from pathlib import Path

import pytest

from pyrig.rig.configs.base.base import ConfigFile
from pyrig.rig.configs.git.gitignore import GitIgnoreConfigFile


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

    def test_lines(
        self,
        my_test_gitignore_config_file: type[GitIgnoreConfigFile],
        tmp_path: Path,
    ) -> None:
        """Test method."""
        with chdir(tmp_path):
            my_test_gitignore_config_file.create_file()
            lines = my_test_gitignore_config_file.lines()
            assert "__pycache__/" in lines

    def test_github_python_gitignore(self) -> None:
        """Test method."""
        github_gitignore = GitIgnoreConfigFile.github_python_gitignore()
        assert "__pycache__/" in github_gitignore

    def test_github_python_gitignore_lines(self) -> None:
        """Test method."""
        github_gitignore = GitIgnoreConfigFile.github_python_gitignore_lines()
        assert "__pycache__/" in github_gitignore

    def test_filename(
        self, my_test_gitignore_config_file: type[GitIgnoreConfigFile]
    ) -> None:
        """Test method."""
        filename = my_test_gitignore_config_file.filename()
        assert filename == "", f"Expected empty string, got {filename}"

    def test_parent_path(
        self,
        my_test_gitignore_config_file: type[GitIgnoreConfigFile],
        tmp_path: Path,
    ) -> None:
        """Test method."""
        with chdir(tmp_path):
            parent_path = my_test_gitignore_config_file.parent_path()
            assert parent_path == Path(), f"Expected Path(), got {parent_path}"

    def test_extension(
        self, my_test_gitignore_config_file: type[GitIgnoreConfigFile]
    ) -> None:
        """Test method."""
        extension = my_test_gitignore_config_file.extension()
        assert extension == "gitignore", f"Expected 'gitignore', got {extension}"
