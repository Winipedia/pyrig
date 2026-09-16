"""module."""

import io
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from ruamel.yaml.comments import CommentedMap

from pyrig.rig.configs.base.yaml import (
    YAML_DUMP,
    YAMLConfigFile,
    YMLConfigFile,
    commented_map,
    represent_str,
)
from pyrig.rig.configs.version_control.remote.workflows.health_check import (
    HealthCheckWorkflowConfigFile,
)


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

        def empty_configs(self) -> dict[str, Any]:
            """Get the empty config."""
            return {}

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


def test_represent_str() -> None:
    """Test function."""
    single_line = represent_str(YAML_DUMP.representer, "value")
    assert single_line.style == '"', "Expected a double-quoted scalar"
    assert single_line.value == "value", "Expected the value to be unchanged"

    multi_line = represent_str(YAML_DUMP.representer, "line1\nline2")
    assert multi_line.style == "|", "Expected a literal block scalar"
    assert multi_line.value == "line1\nline2", "Expected the value to be unchanged"


class TestYMLConfigFile:
    """Test class."""

    def test_extension(self) -> None:
        """Test method."""
        assert issubclass(HealthCheckWorkflowConfigFile, YMLConfigFile)
        extension = HealthCheckWorkflowConfigFile.I.extension()
        assert extension == "yml"


class TestYMLDictConfigFile:
    """Test class."""


def test_commented_map() -> None:
    """Test function."""
    result = commented_map(
        {"contents": "read", "pages": "write"},
        {"pages": "required"},
    )

    assert isinstance(result, CommentedMap)
    assert result == {"contents": "read", "pages": "write"}

    buffer = io.StringIO()
    YAML_DUMP.dump(result, buffer)
    dumped = buffer.getvalue()
    assert '"contents": "read"\n' in dumped
    assert '"pages": "write"  # required' in dumped

    undocumented = commented_map({"contents": "read"}, {})
    assert isinstance(undocumented, CommentedMap)
    buffer_undocumented = io.StringIO()
    YAML_DUMP.dump(undocumented, buffer_undocumented)
    assert "#" not in buffer_undocumented.getvalue()
