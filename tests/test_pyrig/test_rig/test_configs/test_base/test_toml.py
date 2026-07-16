"""module."""

from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from pyrig.rig.configs.base.toml import TOMLConfigFile


@pytest.fixture
def my_test_toml_config_file(
    config_file_factory: Callable[[type[TOMLConfigFile]], type[TOMLConfigFile]],
) -> type[TOMLConfigFile]:
    """Create a test toml config file class with tmp_path."""

    class MyTestTOMLConfigFile(config_file_factory(TOMLConfigFile)):  # ty: ignore[unsupported-base]
        """Test toml config file with tmp_path override."""

        def parent_path(self) -> Path:
            """Get the path to the config file."""
            return Path()

        def stem(self) -> str:
            """Get the stem."""
            return "test_toml"

        def _configs(self) -> dict[str, Any]:
            """Get the config."""
            return {"key": "value"}

    return MyTestTOMLConfigFile


class TestTOMLConfigFile:
    """Test class."""

    def test_pretty_dump(self, my_test_toml_config_file: type[TOMLConfigFile]) -> None:
        """Test method."""
        my_test_toml_config_file().pretty_dump(
            {
                "key": ["value"],
                "repos": [{"repo": "local", "hooks": [{"id": "test"}]}],
            },
        )
        loaded = my_test_toml_config_file().load()
        assert loaded == {
            "key": ["value"],
            "repos": [{"repo": "local", "hooks": [{"id": "test"}]}],
        }, "Expected dump to work"

        # arrays are forced onto multiple lines
        text = my_test_toml_config_file().path().read_text()
        assert "key = [\n" in text, "Expected array to be forced multiline"

    def test__load(self, my_test_toml_config_file: type[TOMLConfigFile]) -> None:
        """Test method."""
        my_test_toml_config_file().validate()
        expected = {"key": "value"}
        actual = my_test_toml_config_file().load()
        assert actual == expected, f"Expected {expected}, got {actual}"

    def test__dump(self, my_test_toml_config_file: type[TOMLConfigFile]) -> None:
        """Test method."""
        my_test_toml_config_file().dump({"key": "value"})
        assert my_test_toml_config_file().load() == {"key": "value"}, (
            "Expected dump to work"
        )

    def test_extension(self, my_test_toml_config_file: type[TOMLConfigFile]) -> None:
        """Test method."""
        assert my_test_toml_config_file().extension() == "toml", "Expected toml"
