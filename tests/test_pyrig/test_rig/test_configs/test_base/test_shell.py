"""module."""

from collections.abc import Callable
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from pyrig.core.subprocesses import Args
from pyrig.rig.configs.base.shell import ShellConfigFile


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

    def test_script(
        self,
        my_test_shell_config_file: type[ShellConfigFile],
    ) -> None:
        """Test method."""
        script = my_test_shell_config_file()
        assert script.script() == 'greet() {\n  echo "Hello, $1"\n}'

    def test_content(self, my_test_shell_config_file: type[ShellConfigFile]) -> None:
        """Test method."""
        script = my_test_shell_config_file()
        expected = (
            f"{script.shebang_line()}\n{script.strict_mode_line()}\n\n{script.script()}"
        )
        assert script.content() == expected

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

    @pytest.mark.parametrize("value", [None, "", "owner/repo with spaces *"])
    def test_required_variable_runtime(
        self,
        my_test_shell_config_file: type[ShellConfigFile],
        mocker: MockerFixture,
        monkeypatch: pytest.MonkeyPatch,
        value: str | None,
    ) -> None:
        """Test method."""
        script = my_test_shell_config_file()
        mocker.patch.object(
            script,
            "required_env_vars",
            return_value=("PYRIG_TEST_REQUIRED",),
        )
        mocker.patch.object(script, "script", return_value="printf 'body reached'")
        if value is None:
            monkeypatch.delenv("PYRIG_TEST_REQUIRED", raising=False)
        else:
            monkeypatch.setenv("PYRIG_TEST_REQUIRED", value)
        result = Args("bash", "-c", script.content()).run(check=False)
        if value:
            assert result.returncode == 0
            assert result.stdout == "body reached"
            assert result.stderr == ""
        else:
            assert result.returncode != 0
            assert result.stdout == ""
            assert "PYRIG_TEST_REQUIRED" in result.stderr


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

        def script(self) -> str:
            """Get the script content."""
            return 'greet() {\n  echo "Hello, $1"\n}'

    return MyTestShellConfigFile
