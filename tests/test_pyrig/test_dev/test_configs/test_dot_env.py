"""module."""

from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from pyrig.dev.configs.dot_env import DotEnvConfigFile
from pyrig.src.testing.assertions import assert_with_msg


@pytest.fixture
def my_test_dotenv_config_file(
    config_file_factory: Callable[[type[DotEnvConfigFile]], type[DotEnvConfigFile]],
) -> type[DotEnvConfigFile]:
    """Create a test dotenv config file class with tmp_path."""

    class MyTestDotEnvConfigFile(config_file_factory(DotEnvConfigFile)):  # type: ignore [misc]
        """Test dotenv config file with tmp_path override."""

    return MyTestDotEnvConfigFile


class TestDotEnvConfigFile:
    """Test class for DotEnvConfigFile."""

    def test_load(self, my_test_dotenv_config_file: type[DotEnvConfigFile]) -> None:
        """Test method for load."""
        # Create the .env file with some content
        my_test_dotenv_config_file.get_path().parent.mkdir(parents=True, exist_ok=True)
        my_test_dotenv_config_file.get_path().write_text(
            "KEY1=value1\nKEY2=value2\nKEY3="
        )

        # Load and verify
        loaded = my_test_dotenv_config_file.load()
        assert_with_msg(loaded["KEY1"] == "value1", "Expected KEY1=value1")
        assert_with_msg(loaded["KEY2"] == "value2", "Expected KEY2=value2")
        assert_with_msg(loaded["KEY3"] == "", "Expected KEY3 to be empty string")

    def test_dump(self, my_test_dotenv_config_file: type[DotEnvConfigFile]) -> None:
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
        assert_with_msg(
            my_test_dotenv_config_file.get_file_extension() == "env",
            "Expected env",
        )

    def test_get_filename(
        self, my_test_dotenv_config_file: type[DotEnvConfigFile]
    ) -> None:
        """Test method for get_filename."""
        # Should return empty string so path becomes .env not env.env
        expected = ""
        actual = my_test_dotenv_config_file.get_filename()
        assert_with_msg(actual == expected, f"Expected {expected}, got {actual}")

    def test_get_parent_path(
        self, my_test_dotenv_config_file: type[DotEnvConfigFile]
    ) -> None:
        """Test method for get_parent_path."""
        # Should return Path() (root)
        expected = Path()
        actual = my_test_dotenv_config_file.get_parent_path()
        assert_with_msg(actual == expected, f"Expected {expected}, got {actual}")

    def test_get_configs(
        self, my_test_dotenv_config_file: type[DotEnvConfigFile]
    ) -> None:
        """Test method for get_configs."""
        # Should return empty dict
        expected: dict[str, Any] = {}
        actual = my_test_dotenv_config_file.get_configs()
        assert_with_msg(actual == expected, f"Expected {expected}, got {actual}")

    def test_is_correct(
        self, my_test_dotenv_config_file: type[DotEnvConfigFile]
    ) -> None:
        """Test method for is_correct."""
        # Create the file
        my_test_dotenv_config_file.get_path().parent.mkdir(parents=True, exist_ok=True)
        my_test_dotenv_config_file.get_path().touch()

        # Should be correct if file exists (even if empty)
        assert_with_msg(
            my_test_dotenv_config_file.is_correct(),
            "Expected .env file to be correct when it exists",
        )

        # Remove the file
        my_test_dotenv_config_file.get_path().unlink()

        # Should still be correct because get_configs returns empty dict
        # and is_correct_recursively({}, {}) returns True (empty subset of empty)
        # The implementation: super().is_correct() or cls.get_path().exists()
        # Since get_configs() is {} and load() would be {}, they match
        assert_with_msg(
            my_test_dotenv_config_file.is_correct(),
            "Expected .env file to be correct even when doesn't exist (empty)",
        )
