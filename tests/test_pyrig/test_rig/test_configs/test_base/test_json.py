"""module."""

from collections.abc import Callable
from pathlib import Path
from typing import Any, override

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from pyrig.rig.configs.base.json import JSONDictConfigFile


class TestJSONConfigFile:
    """Test class."""

    def test__dump(self, my_test_json_config_file: type[JSONDictConfigFile]) -> None:
        """Test method."""
        my_test_json_config_file().dump({"key": "value"})
        loaded = my_test_json_config_file().load()
        assert loaded == {"key": "value"}

    def test__load(self, my_test_json_config_file: type[JSONDictConfigFile]) -> None:
        """Test method."""
        my_test_json_config_file().validate()
        loaded = my_test_json_config_file().load()
        assert loaded == {"key": "value"}

    def test_extension(
        self,
        my_test_json_config_file: type[JSONDictConfigFile],
    ) -> None:
        """Test method."""
        extension = my_test_json_config_file().extension()
        assert extension == "json"

    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        config=st.dictionaries(
            st.text(max_size=10),
            st.recursive(
                st.one_of(
                    st.none(),
                    st.booleans(),
                    st.integers(),
                    st.text(max_size=20),
                ),
                lambda children: st.one_of(
                    st.lists(children, max_size=4),
                    st.dictionaries(st.text(max_size=10), children, max_size=4),
                ),
                max_leaves=20,
            ),
            max_size=4,
        ),
    )
    def test_round_trip_generated_configs(
        self,
        my_test_json_config_file: type[JSONDictConfigFile],
        config: dict[str, Any],
    ) -> None:
        """Each dump replaces the fixture's file and clears its cached load."""
        my_test_json_config_file().dump(config)
        assert my_test_json_config_file.load() == config


class TestJSONDictConfigFile:
    """Test class."""


@pytest.fixture
def my_test_json_config_file(
    config_file_factory: Callable[[type[JSONDictConfigFile]], type[JSONDictConfigFile]],
) -> type[JSONDictConfigFile]:
    """Create a test json config file class with tmp_path."""

    class MyTestJSONDictConfigFile(config_file_factory(JSONDictConfigFile)):  # ty: ignore[unsupported-base]
        """Test json config file."""

        @override
        def stem(self) -> str:
            """Get the stem."""
            return "test_json"

        @override
        def parent_path(self) -> Path:
            """Get the parent path."""
            return Path()

        @override
        def _configs(self) -> dict[str, Any]:
            """Get the configs."""
            return {"key": "value"}

    return MyTestJSONDictConfigFile
