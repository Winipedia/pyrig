"""module."""

from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from pyrig.rig.configs.base.yaml import YamlConfigFile


@pytest.fixture
def my_test_yaml_config_file(
    config_file_factory: Callable[
        [type[YamlConfigFile[dict[str, Any]]]], type[YamlConfigFile[dict[str, Any]]]
    ],
) -> type[YamlConfigFile[dict[str, Any]]]:
    """Create a test yaml config file class with tmp_path."""

    class MyTestYamlConfigFile(config_file_factory(YamlConfigFile)):  # type: ignore [misc]
        """Test yaml config file with tmp_path override."""

        def parent_path(self) -> Path:
            """Get the path to the config file."""
            return Path()

        def _configs(self) -> dict[str, Any]:
            """Get the config."""
            return {"key": "value"}

    return MyTestYamlConfigFile


class TestYamlConfigFile:
    """Test class."""

    def test__load(
        self, my_test_yaml_config_file: type[YamlConfigFile[dict[str, Any]]]
    ) -> None:
        """Test method."""
        my_test_yaml_config_file().validate()
        expected = {"key": "value"}
        actual = my_test_yaml_config_file().load()
        assert actual == expected, f"Expected {expected}, got {actual}"

    def test__dump(
        self, my_test_yaml_config_file: type[YamlConfigFile[dict[str, Any]]]
    ) -> None:
        """Test method."""
        my_test_yaml_config_file().dump({"key": "value"})
        assert my_test_yaml_config_file().load() == {"key": "value"}, (
            "Expected dump to work"
        )

    def test_extension(
        self, my_test_yaml_config_file: type[YamlConfigFile[dict[str, Any]]]
    ) -> None:
        """Test method."""
        assert my_test_yaml_config_file().extension() == "yaml", "Expected yaml"
