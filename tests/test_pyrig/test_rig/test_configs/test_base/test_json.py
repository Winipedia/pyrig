"""module."""

from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from pyrig.rig.configs.base.json import JsonConfigFile


@pytest.fixture
def my_test_json_config_file(
    config_file_factory: Callable[[type[JsonConfigFile]], type[JsonConfigFile]],
) -> type[JsonConfigFile]:
    """Create a test json config file class with tmp_path."""

    class MyTestJsonConfigFile(config_file_factory(JsonConfigFile)):  # type: ignore [misc]
        """Test json config file."""

        def parent_path(self) -> Path:
            """Get the parent path."""
            return Path()

        def _configs(self) -> dict[str, Any] | list[Any]:
            """Get the configs."""
            return {"key": "value"}

    return MyTestJsonConfigFile


class TestJsonConfigFile:
    """Test class."""

    def test__load(self, my_test_json_config_file: type[JsonConfigFile]) -> None:
        """Test method."""
        my_test_json_config_file().validate()
        loaded = my_test_json_config_file().load()
        assert loaded == {"key": "value"}

    def test__dump(self, my_test_json_config_file: type[JsonConfigFile]) -> None:
        """Test method."""
        my_test_json_config_file().dump({"key": "value"})
        loaded = my_test_json_config_file().load()
        assert loaded == {"key": "value"}

    def test_extension(self, my_test_json_config_file: type[JsonConfigFile]) -> None:
        """Test method."""
        extension = my_test_json_config_file().extension()
        assert extension == "json"
