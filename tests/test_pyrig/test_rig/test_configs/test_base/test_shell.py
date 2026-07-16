"""module."""

import stat
from collections.abc import Callable
from contextlib import chdir
from pathlib import Path

import pytest

from pyrig.rig.configs.base.shell import ShellConfigFile


@pytest.fixture
def my_test_shell_config_file(
    config_file_factory: Callable[[type[ShellConfigFile]], type[ShellConfigFile]],
) -> type[ShellConfigFile]:
    """Create a test shell config file class with tmp_path."""

    class MyTestShellConfigFile(config_file_factory(ShellConfigFile)):  # ty: ignore[unsupported-base]
        """Test shell config file with tmp_path override."""

        def stem(self) -> str:
            """Get the stem."""
            return "test_script"

        def parent_path(self) -> Path:
            """Get the parent path."""
            return Path()

        def script_content(self) -> str:
            """Get the script content."""
            return 'greet() {\n  echo "Hello, $1"\n}'

    return MyTestShellConfigFile


class TestShellConfigFile:
    """Test class."""

    def test_extension(self, my_test_shell_config_file: type[ShellConfigFile]) -> None:
        """Test method."""
        expected = "sh"
        actual = my_test_shell_config_file().extension()
        assert actual == expected

    def test_shebang_line(
        self,
        my_test_shell_config_file: type[ShellConfigFile],
    ) -> None:
        """Test method."""
        assert my_test_shell_config_file().shebang_line() == "#!/usr/bin/env bash"

    def test_strict_mode_line(
        self,
        my_test_shell_config_file: type[ShellConfigFile],
    ) -> None:
        """Test method."""
        assert my_test_shell_config_file().strict_mode_line() == "set -euo pipefail"

    def test_script_content(
        self,
        my_test_shell_config_file: type[ShellConfigFile],
    ) -> None:
        """Test method."""
        script = my_test_shell_config_file()
        assert script.script_content() == 'greet() {\n  echo "Hello, $1"\n}'

    def test_content(self, my_test_shell_config_file: type[ShellConfigFile]) -> None:
        """Test method."""
        script = my_test_shell_config_file()
        expected = (
            f"{script.shebang_line()}\n{script.strict_mode_line()}\n\n"
            f"{script.script_content()}"
        )
        assert script.content() == expected

    def test_create_file(
        self,
        my_test_shell_config_file: type[ShellConfigFile],
        tmp_path: Path,
    ) -> None:
        """Test method."""
        with chdir(tmp_path):
            script = my_test_shell_config_file()
            script.create_file()
            path = script.path()
            assert path.exists()
            assert path.stat().st_mode & stat.S_IXUSR
            assert path.stat().st_mode & stat.S_IXGRP
            assert path.stat().st_mode & stat.S_IXOTH
