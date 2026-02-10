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

        @classmethod
        def get_parent_path(cls) -> Path:
            """Get the parent path."""
            return Path()

        @classmethod
        def _get_configs(cls) -> dict[str, Any] | list[Any]:
            """Get the configs."""
            return {"key": "value"}

    return MyTestJsonConfigFile


class TestJsonConfigFile:
    """Test class."""

    def test__load(self, my_test_json_config_file: type[JsonConfigFile]) -> None:
        """Test method."""
        my_test_json_config_file()
        loaded = my_test_json_config_file.load()
        assert loaded == {"key": "value"}

    def test__dump(self, my_test_json_config_file: type[JsonConfigFile]) -> None:
        """Test method."""
        my_test_json_config_file.dump({"key": "value"})
        loaded = my_test_json_config_file.load()
        assert loaded == {"key": "value"}

    def test_get_file_extension(self) -> None:
        """Test method."""
        extension = JsonConfigFile.get_file_extension()
        assert extension == "json"
