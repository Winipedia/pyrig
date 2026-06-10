"""module."""

from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from pyrig.rig.configs.base.json import JSONListConfigFile


@pytest.fixture
def my_test_json_config_file(
    config_file_factory: Callable[[type[JSONListConfigFile]], type[JSONListConfigFile]],
) -> type[JSONListConfigFile]:
    """Create a test json config file class with tmp_path."""

    class MyTestJSONListConfigFile(config_file_factory(JSONListConfigFile)):  # ty: ignore[unsupported-base]
        """Test json config file."""

        def stem(self) -> str:
            """Get the stem."""
            return "test_json"

        def parent_path(self) -> Path:
            """Get the parent path."""
            return Path()

        def _configs(self) -> list[dict[str, Any]]:
            """Get the configs."""
            return [{"key": "value"}]

    return MyTestJSONListConfigFile


class TestJSONConfigFile:
    """Test class."""

    def test__load(self, my_test_json_config_file: type[JSONListConfigFile]) -> None:
        """Test method."""
        my_test_json_config_file().validate()
        loaded = my_test_json_config_file().load()
        assert loaded == [{"key": "value"}]

    def test__dump(self, my_test_json_config_file: type[JSONListConfigFile]) -> None:
        """Test method."""
        my_test_json_config_file().dump([{"key": "value"}])
        loaded = my_test_json_config_file().load()
        assert loaded == [{"key": "value"}]

    def test_extension(
        self, my_test_json_config_file: type[JSONListConfigFile]
    ) -> None:
        """Test method."""
        extension = my_test_json_config_file().extension()
        assert extension == "json"


class TestJSONListConfigFile:
    """Test class."""
