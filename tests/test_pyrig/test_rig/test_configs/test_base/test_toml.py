"""module."""

from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from pyrig.rig.configs.base.toml import TomlConfigFile


@pytest.fixture
def my_test_toml_config_file(
    config_file_factory: Callable[[type[TomlConfigFile]], type[TomlConfigFile]],
) -> type[TomlConfigFile]:
    """Create a test toml config file class with tmp_path."""

    class MyTestTomlConfigFile(config_file_factory(TomlConfigFile)):  # type: ignore [misc]
        """Test toml config file with tmp_path override."""

        def parent_path(self) -> Path:
            """Get the path to the config file."""
            return Path()

        def _configs(self) -> dict[str, Any]:
            """Get the config."""
            return {"key": "value"}

    return MyTestTomlConfigFile


class TestTomlConfigFile:
    """Test class."""

    def test_prettify_value(
        self, my_test_toml_config_file: type[TomlConfigFile]
    ) -> None:
        """Test method."""
        # scalar passthrough
        assert my_test_toml_config_file().prettify_value("hello") == "hello"
        assert my_test_toml_config_file().prettify_value(1) == 1
        assert my_test_toml_config_file().prettify_value(value=True) is True

        # list of scalars becomes multiline array
        result = my_test_toml_config_file().prettify_value(["a", "b"])
        assert list(result) == ["a", "b"]

        # dict becomes inline table
        result = my_test_toml_config_file().prettify_value({"k": "v"})
        assert result["k"] == "v"

        # nested: list of dicts with nested lists
        result = my_test_toml_config_file().prettify_value(
            [{"repo": "local", "hooks": [{"id": "test"}]}]
        )
        assert result[0]["repo"] == "local"
        assert result[0]["hooks"][0]["id"] == "test"

    def test_prettify_dict(
        self, my_test_toml_config_file: type[TomlConfigFile]
    ) -> None:
        """Test method."""
        expected = {"key": ["value"]}
        actual = my_test_toml_config_file().prettify_dict({"key": ["value"]})
        assert actual == expected, f"Expected {expected}, got {actual}"

    def test_pretty_dump(self, my_test_toml_config_file: type[TomlConfigFile]) -> None:
        """Test method."""
        my_test_toml_config_file().pretty_dump({"key": ["value"]})
        assert my_test_toml_config_file().load() == {"key": ["value"]}, (
            "Expected dump to work"
        )

    def test__load(self, my_test_toml_config_file: type[TomlConfigFile]) -> None:
        """Test method."""
        my_test_toml_config_file().validate()
        expected = {"key": "value"}
        actual = my_test_toml_config_file().load()
        assert actual == expected, f"Expected {expected}, got {actual}"

    def test__dump(self, my_test_toml_config_file: type[TomlConfigFile]) -> None:
        """Test method."""
        my_test_toml_config_file().dump({"key": "value"})
        assert my_test_toml_config_file().load() == {"key": "value"}, (
            "Expected dump to work"
        )

    def test_extension(self, my_test_toml_config_file: type[TomlConfigFile]) -> None:
        """Test method."""
        assert my_test_toml_config_file().extension() == "toml", "Expected toml"
