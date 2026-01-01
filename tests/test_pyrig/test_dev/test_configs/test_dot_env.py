"""module."""

from collections.abc import Callable
from contextlib import chdir
from pathlib import Path
from typing import Any

import pytest

from pyrig.dev.configs.dot_env import DotEnvConfigFile


@pytest.fixture
def my_test_dotenv_config_file(
    config_file_factory: Callable[[type[DotEnvConfigFile]], type[DotEnvConfigFile]],
) -> type[DotEnvConfigFile]:
    """Create a test dotenv config file class with tmp_path."""

    class MyTestDotEnvConfigFile(config_file_factory(DotEnvConfigFile)):  # type: ignore [misc]
        """Test dotenv config file with tmp_path override."""

    return MyTestDotEnvConfigFile


class TestDotEnvConfigFile:
    """Test class."""

    def test__load(self, my_test_dotenv_config_file: type[DotEnvConfigFile]) -> None:
        """Test method for load."""
        # Create the .env file with some content
        my_test_dotenv_config_file.get_path().parent.mkdir(parents=True, exist_ok=True)
        my_test_dotenv_config_file.get_path().write_text(
            "KEY1=value1\nKEY2=value2\nKEY3="
        )

        # Load and verify
        loaded = my_test_dotenv_config_file.load()
        assert loaded["KEY1"] == "value1", "Expected KEY1=value1"
        assert loaded["KEY2"] == "value2", "Expected KEY2=value2"
        assert loaded["KEY3"] == "", "Expected KEY3 to be empty string"

    def test__dump(self, my_test_dotenv_config_file: type[DotEnvConfigFile]) -> None:
        """Test method for dump."""
        # dump should raise ValueError if config is not empty (truthy)
        with pytest.raises(ValueError, match=r"Cannot dump .* to \.env file"):
            my_test_dotenv_config_file.dump({"key": "value"})

        # dump with empty dict should NOT raise ValueError (empty dict is falsy)
        # This is the expected behavior based on the implementation
        my_test_dotenv_config_file.dump({})

    def test_get_file_extension(
        self, my_test_dotenv_config_file: type[DotEnvConfigFile]
    ) -> None:
        """Test method for get_file_extension."""
        assert my_test_dotenv_config_file.get_file_extension() == "env", "Expected env"

    def test_get_filename(
        self, my_test_dotenv_config_file: type[DotEnvConfigFile]
    ) -> None:
        """Test method for get_filename."""
        # Should return empty string so path becomes .env not env.env
        expected = ""
        actual = my_test_dotenv_config_file.get_filename()
        assert actual == expected, f"Expected {expected}, got {actual}"

    def test_get_parent_path(
        self,
        my_test_dotenv_config_file: type[DotEnvConfigFile],
        tmp_path: Path,
    ) -> None:
        """Test method for get_parent_path."""
        # Should return Path() (root)
        with chdir(tmp_path):
            expected = Path()
            actual = my_test_dotenv_config_file.get_parent_path()
            assert actual == expected, f"Expected {expected}, got {actual}"

    def test_get_configs(
        self, my_test_dotenv_config_file: type[DotEnvConfigFile]
    ) -> None:
        """Test method for get_configs."""
        # Should return empty dict
        expected: dict[str, Any] = {}
        actual = my_test_dotenv_config_file.get_configs()
        assert actual == expected, f"Expected {expected}, got {actual}"

    def test_is_correct(
        self, my_test_dotenv_config_file: type[DotEnvConfigFile]
    ) -> None:
        """Test method for is_correct."""
        # Create the file
        my_test_dotenv_config_file.get_path().parent.mkdir(parents=True, exist_ok=True)
        my_test_dotenv_config_file.get_path().touch()

        # Should be correct if file exists (even if empty)
        assert my_test_dotenv_config_file.is_correct(), (
            "Expected .env file to be correct when it exists"
        )
