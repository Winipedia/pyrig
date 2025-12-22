"""module."""

from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from pyrig.dev.configs.base.yaml import YamlConfigFile
from pyrig.src.testing.assertions import assert_with_msg


@pytest.fixture
def my_test_yaml_config_file(
    config_file_factory: Callable[[type[YamlConfigFile]], type[YamlConfigFile]],
) -> type[YamlConfigFile]:
    """Create a test yaml config file class with tmp_path."""

    class MyTestYamlConfigFile(config_file_factory(YamlConfigFile)):  # type: ignore [misc]
        """Test yaml config file with tmp_path override."""

        @classmethod
        def get_parent_path(cls) -> Path:
            """Get the path to the config file."""
            return Path()

        @classmethod
        def get_configs(cls) -> dict[str, Any]:
            """Get the config."""
            return {"key": "value"}

    return MyTestYamlConfigFile


class TestYamlConfigFile:
    """Test class."""

    def test_load(self, my_test_yaml_config_file: type[YamlConfigFile]) -> None:
        """Test method for load."""
        my_test_yaml_config_file()
        expected = {"key": "value"}
        actual = my_test_yaml_config_file.load()
        assert_with_msg(actual == expected, f"Expected {expected}, got {actual}")

    def test_dump(self, my_test_yaml_config_file: type[YamlConfigFile]) -> None:
        """Test method for dump."""
        my_test_yaml_config_file.dump({"key": "value"})
        assert_with_msg(
            my_test_yaml_config_file.load() == {"key": "value"},
            "Expected dump to work",
        )

    def test_get_file_extension(
        self, my_test_yaml_config_file: type[YamlConfigFile]
    ) -> None:
        """Test method for get_file_extension."""
        assert_with_msg(
            my_test_yaml_config_file.get_file_extension() == "yaml",
            "Expected yaml",
        )
