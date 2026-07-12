"""module."""

from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from pyrig.rig.configs.base.yaml import _YAML, YAMLConfigFile, _represent_str


@pytest.fixture
def my_test_yaml_config_file(
    config_file_factory: Callable[
        [type[YAMLConfigFile[dict[str, Any]]]],
        type[YAMLConfigFile[dict[str, Any]]],
    ],
) -> type[YAMLConfigFile[dict[str, Any]]]:
    """Create a test yaml config file class with tmp_path."""

    class MyTestYAMLConfigFile(config_file_factory(YAMLConfigFile)):  # ty: ignore[unsupported-base]
        """Test yaml config file with tmp_path override."""

        def parent_path(self) -> Path:
            """Get the path to the config file."""
            return Path()

        def stem(self) -> str:
            """Get the stem."""
            return "test_yaml"

        def _configs(self) -> dict[str, Any]:
            """Get the config."""
            return {"key": "value"}

    return MyTestYAMLConfigFile


class TestYAMLConfigFile:
    """Test class."""

    def test__load(
        self,
        my_test_yaml_config_file: type[YAMLConfigFile[dict[str, Any]]],
    ) -> None:
        """Test method."""
        my_test_yaml_config_file().validate()
        expected = {"key": "value"}
        actual = my_test_yaml_config_file().load()
        assert actual == expected, f"Expected {expected}, got {actual}"

    def test__dump(
        self,
        my_test_yaml_config_file: type[YAMLConfigFile[dict[str, Any]]],
    ) -> None:
        """Test method."""
        my_test_yaml_config_file().dump({"key": "value"})
        assert my_test_yaml_config_file().load() == {"key": "value"}, (
            "Expected dump to work"
        )

    def test__dump_multiline_string_as_literal_block(
        self,
        my_test_yaml_config_file: type[YAMLConfigFile[dict[str, Any]]],
    ) -> None:
        """Test method."""
        config_file = my_test_yaml_config_file()
        value = "line1\nline2"
        config_file.dump({"key": value})
        content = config_file.path().read_text()
        assert '"key": |-' in content, "Expected a literal block scalar"
        assert config_file.load() == {"key": value}, "Expected round-trip to work"

    def test_extension(
        self,
        my_test_yaml_config_file: type[YAMLConfigFile[dict[str, Any]]],
    ) -> None:
        """Test method."""
        assert my_test_yaml_config_file().extension() == "yaml", "Expected yaml"


def test__represent_str() -> None:
    """Test function."""
    single_line = _represent_str(_YAML.representer, "value")
    assert single_line.style == '"', "Expected a double-quoted scalar"
    assert single_line.value == "value", "Expected the value to be unchanged"

    multi_line = _represent_str(_YAML.representer, "line1\nline2")
    assert multi_line.style == "|", "Expected a literal block scalar"
    assert multi_line.value == "line1\nline2", "Expected the value to be unchanged"
