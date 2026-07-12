"""module."""

from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
import tomlkit
from tomlkit import TOMLDocument

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

    def test_pretty_dump_preserves_comments_on_merge(
        self,
        my_test_toml_config_file: type[TOMLConfigFile],
    ) -> None:
        """Test method."""
        instance = my_test_toml_config_file()
        instance.path().write_text(
            '# top comment\nkey = ["value"]\n# standalone comment\n',
        )
        loaded = instance.load()
        loaded["extra"] = "added"
        instance.pretty_dump(loaded)

        text = instance.path().read_text()
        assert "# top comment" in text, "Expected top-level comment to survive"
        assert "# standalone comment" in text, "Expected standalone comment to survive"
        assert 'extra = "added"' in text, "Expected the new key to be written"

    def test_document(self, my_test_toml_config_file: type[TOMLConfigFile]) -> None:
        """Test method."""
        doc = my_test_toml_config_file().document(
            {"project": {"name": "demo"}, "repos": [{"repo": "local"}]},
        )
        assert isinstance(doc, TOMLDocument)
        assert doc["project"]["name"] == "demo"
        assert doc["repos"][0]["repo"] == "local"

        # a fresh dict is already forced multiline by document() itself
        doc = my_test_toml_config_file().document({"deps": ["a", "b"]})
        assert doc["deps"].as_string() == '[\n    "a",\n    "b",\n]'

    def test_to_multiline(
        self,
        my_test_toml_config_file: type[TOMLConfigFile],
    ) -> None:
        """Test method."""
        instance = my_test_toml_config_file()
        array = tomlkit.array()
        array.extend(["a", "b"])
        assert array.as_string() == '["a", "b"]'

        instance.to_multiline(array)
        assert array.as_string() == '[\n    "a",\n    "b",\n]'

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
