"""module."""

from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from pyrig.dev.configs.base.toml import TomlConfigFile


@pytest.fixture
def my_test_toml_config_file(
    config_file_factory: Callable[[type[TomlConfigFile]], type[TomlConfigFile]],
) -> type[TomlConfigFile]:
    """Create a test toml config file class with tmp_path."""

    class MyTestTomlConfigFile(config_file_factory(TomlConfigFile)):  # type: ignore [misc]
        """Test toml config file with tmp_path override."""

        @classmethod
        def get_parent_path(cls) -> Path:
            """Get the path to the config file."""
            return Path()

        @classmethod
        def get_configs(cls) -> dict[str, Any]:
            """Get the config."""
            return {"key": "value"}

    return MyTestTomlConfigFile


class TestTomlConfigFile:
    """Test class."""

    def test_prettify_dict(
        self, my_test_toml_config_file: type[TomlConfigFile]
    ) -> None:
        """Test method."""
        expected = {"key": ["value"]}
        actual = my_test_toml_config_file.prettify_dict({"key": ["value"]})
        assert actual == expected, f"Expected {expected}, got {actual}"

    def test_pretty_dump(self, my_test_toml_config_file: type[TomlConfigFile]) -> None:
        """Test method."""
        my_test_toml_config_file.pretty_dump({"key": ["value"]})
        assert my_test_toml_config_file.load() == {"key": ["value"]}, (
            "Expected dump to work"
        )

    def test__load(self, my_test_toml_config_file: type[TomlConfigFile]) -> None:
        """Test method for load."""
        my_test_toml_config_file()
        expected = {"key": "value"}
        actual = my_test_toml_config_file.load()
        assert actual == expected, f"Expected {expected}, got {actual}"

    def test__dump(self, my_test_toml_config_file: type[TomlConfigFile]) -> None:
        """Test method for dump."""
        my_test_toml_config_file.dump({"key": "value"})
        assert my_test_toml_config_file.load() == {"key": "value"}, (
            "Expected dump to work"
        )

    def test_get_file_extension(
        self, my_test_toml_config_file: type[TomlConfigFile]
    ) -> None:
        """Test method for get_file_extension."""
        assert my_test_toml_config_file.get_file_extension() == "toml", "Expected toml"
