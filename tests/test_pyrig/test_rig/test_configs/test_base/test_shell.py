"""module."""

from collections.abc import Callable
from pathlib import Path
from typing import override

import pytest
from pytest_mock import MockerFixture

from pyrig.rig.configs.base.shell import ShellConfigFile


class TestShellConfigFile:
    """Test class."""

    def test_content(self, my_test_shell_config_file: type[ShellConfigFile]) -> None:
        """Test method."""
        script = my_test_shell_config_file()
        expected = (
            f"{script.shebang_line()}\n{script.strict_mode_line()}\n\n{script.script()}"
        )
        assert script.content() == expected

    def test_extension(self, my_test_shell_config_file: type[ShellConfigFile]) -> None:
        """Test method."""
        expected = "sh"
        actual = my_test_shell_config_file().extension()
        assert actual == expected

    @pytest.mark.parametrize("variables", [(), ("FIRST", "SECOND")])
    def test_global_content(
        self,
        my_test_shell_config_file: type[ShellConfigFile],
        mocker: MockerFixture,
        variables: tuple[str, ...],
    ) -> None:
        """Test method."""
        script = my_test_shell_config_file()
        mocker.patch.object(script, "required_env_vars", return_value=variables)
        expected = "#!/usr/bin/env bash\nset -euo pipefail"
        if variables:
            expected += '\n\n: "${FIRST:?}"\n: "${SECOND:?}"'
        assert script.global_content() == expected
        assert script.content() == f"{expected}\n\n{script.script()}"

    @pytest.mark.parametrize(
        ("variables", "expected"),
        [
            ((), ""),
            (("FIRST",), ': "${FIRST:?}"'),
            (("FIRST", "SECOND"), ': "${FIRST:?}"\n: "${SECOND:?}"'),
        ],
    )
    def test_required_env_var_checks(
        self,
        my_test_shell_config_file: type[ShellConfigFile],
        mocker: MockerFixture,
        variables: tuple[str, ...],
        expected: str,
    ) -> None:
        """Test method."""
        script = my_test_shell_config_file()
        mocker.patch.object(script, "required_env_vars", return_value=variables)
        assert script.required_env_var_checks() == expected

    def test_required_env_vars(
        self,
        my_test_shell_config_file: type[ShellConfigFile],
    ) -> None:
        """Test method."""
        assert my_test_shell_config_file().required_env_vars() == ()

    def test_script(
        self,
        my_test_shell_config_file: type[ShellConfigFile],
    ) -> None:
        """Test method."""
        script = my_test_shell_config_file()
        assert script.script() == 'greet() {\n  echo "Hello, $1"\n}'

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


@pytest.fixture
def my_test_shell_config_file(
    config_file_factory: Callable[[type[ShellConfigFile]], type[ShellConfigFile]],
) -> type[ShellConfigFile]:
    """Create a test shell config file class with tmp_path."""

    class MyTestShellConfigFile(config_file_factory(ShellConfigFile)):  # ty: ignore[unsupported-base]
        """Test shell config file with tmp_path override."""

        @override
        def stem(self) -> str:
            """Get the stem."""
            return "test_script"

        @override
        def parent_path(self) -> Path:
            """Get the parent path."""
            return Path()

        @override
        def script(self) -> str:
            """Get the script content."""
            return 'greet() {\n  echo "Hello, $1"\n}'

    return MyTestShellConfigFile
