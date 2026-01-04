"""module."""

from collections.abc import Callable

import pytest

from pyrig.dev.configs.base.typed import TypedConfigFile


@pytest.fixture
def my_test_typed_config_file(
    config_file_factory: Callable[[type[TypedConfigFile]], type[TypedConfigFile]],
) -> type[TypedConfigFile]:
    """Create a test typed config file class with tmp_path."""

    class MyTestTypedConfigFile(config_file_factory(TypedConfigFile)):  # type: ignore [misc]
        """Test typed config file with tmp_path override."""

    return MyTestTypedConfigFile


class TestTypedConfigFile:
    """Test class."""

    def test_get_file_extension(
        self, my_test_typed_config_file: type[TypedConfigFile]
    ) -> None:
        """Test method for get_file_extension."""
        expected = "typed"
        actual = my_test_typed_config_file.get_file_extension()
        assert actual == expected, f"Expected {expected}, got {actual}"

    def test__load(self, my_test_typed_config_file: type[TypedConfigFile]) -> None:
        """Test method for load."""
        loaded = my_test_typed_config_file.load()
        assert loaded == {}, "Expected load to return empty dict"

    def test__dump(self, my_test_typed_config_file: type[TypedConfigFile]) -> None:
        """Test method for dump."""
        # assert dumps empty dict successfully
        my_test_typed_config_file.dump({})
        assert my_test_typed_config_file.load() == {}, (
            "Expected dump to work with empty dict"
        )
        # assert raises ValueError if config is not empty
        with pytest.raises(ValueError, match=r"Cannot dump to py\.typed file"):
            my_test_typed_config_file.dump({"key": "value"})

    def test__get_configs(
        self, my_test_typed_config_file: type[TypedConfigFile]
    ) -> None:
        """Test method for get_configs."""
        configs = my_test_typed_config_file.get_configs()
        assert configs == {}, "Expected get_configs to return empty dict"
