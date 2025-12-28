"""module."""

import copy
from collections.abc import Callable
from pathlib import Path
from typing import Any, ClassVar

import pytest
from pytest_mock import MockFixture

from pyrig.dev.configs.base.base import (
    ConfigFile,
)
from pyrig.src.modules.package import (
    get_all_nonabst_subcls_from_mod_in_all_deps_depen_on_dep,
)
from pyrig.src.testing.assertions import assert_with_msg


@pytest.fixture
def my_test_config_file(
    config_file_factory: Callable[[type[ConfigFile]], type[ConfigFile]],
) -> type[ConfigFile]:
    """Create a test config file class with tmp_path."""

    class MyTestConfigFile(config_file_factory(ConfigFile)):  # type: ignore [misc]
        """Test config file with tmp_path override."""

        STORAGE_DICT: ClassVar[dict[str, Any]] = {
            "key0": "value0",
            "key1": "value1",
            "key2": {"key3": "value3"},
            "key4": [["value4"], {"key5": "value5", "key6": "value6"}],
        }

        @classmethod
        def get_file_extension(cls) -> str:
            """Get the file extension of the config file."""
            return "txt"

        @classmethod
        def _load(cls) -> dict[str, Any] | list[Any]:
            """Load the config file."""
            return copy.deepcopy(cls.STORAGE_DICT)

        @classmethod
        def _dump(cls, config: dict[str, Any] | list[Any]) -> None:
            """Dump the config file."""
            if not isinstance(config, dict):
                msg = f"Cannot dump {config} to txt file."
                raise TypeError(msg)
            cls.STORAGE_DICT = config

        @classmethod
        def get_parent_path(cls) -> Path:
            """Get the path to the config file."""
            return Path("parent_dir")

        @classmethod
        def get_configs(cls) -> dict[str, Any]:
            """Get the config."""
            return {
                "key1": "value1",
                "key2": {"key3": "value3"},
                "key4": [["notvalue4", "extra_value"], {"key5": "notvalue5"}],
                "key7": "value7",
            }

    return MyTestConfigFile


class TestConfigFile:
    """Test class."""

    def test__load(self, my_test_config_file: type[ConfigFile]) -> None:
        """Test method."""
        loaded = my_test_config_file._load()  # noqa: SLF001
        assert loaded["key0"] == "value0"

        # assert cache works
        # _dump to change STORAGE_DICT
        loaded = my_test_config_file.load()
        assert loaded["key0"] == "value0"
        loaded = copy.deepcopy(loaded)
        loaded["key0"] = "new_value0"
        my_test_config_file._dump(loaded)  # noqa: SLF001
        loaded = my_test_config_file.load()
        assert loaded["key0"] == "value0"  # cache still has old value

        # clear cache and assert new value
        my_test_config_file.load.cache_clear()
        loaded = my_test_config_file.load()
        assert loaded["key0"] == "new_value0"

    def test__dump(self, my_test_config_file: type[ConfigFile]) -> None:
        """Test method."""
        my_test_config_file._dump({"key": "value"})  # noqa: SLF001
        assert my_test_config_file.load()["key"] == "value"

        # dump and assert cache is cleared
        my_test_config_file.dump({"key": "new_value"})
        assert my_test_config_file.load()["key"] == "new_value"

    def test_get_priority(self) -> None:
        """Test method."""
        assert ConfigFile.get_priority() == 0

    def test_get_priority_subclasses(self) -> None:
        """Test method."""
        priority_subclasses = ConfigFile.get_priority_subclasses()
        assert isinstance(priority_subclasses, list)
        assert all(issubclass(cf, ConfigFile) for cf in priority_subclasses)

    def test_init_subclasses(
        self, mocker: MockFixture, my_test_config_file: type[ConfigFile]
    ) -> None:
        """Test method."""
        mock = mocker.patch.object(ConfigFile, "__init__", return_value=None)
        ConfigFile.init_subclasses(my_test_config_file)
        mock.assert_called_once()

    def test_init_all_subclasses(self, mocker: MockFixture) -> None:
        """Test method."""
        num_subclasses = ConfigFile.get_all_subclasses()
        mock = mocker.patch.object(ConfigFile, "__init__", return_value=None)
        ConfigFile.init_all_subclasses()
        assert mock.call_count == len(num_subclasses)

    def test_init_priority_subclasses(self, mocker: MockFixture) -> None:
        """Test method."""
        num_priority_subclasses = ConfigFile.get_priority_subclasses()
        mock = mocker.patch.object(ConfigFile, "__init__", return_value=None)
        ConfigFile.init_priority_subclasses()
        assert mock.call_count == len(num_priority_subclasses)

    def test_get_extension_sep(self) -> None:
        """Test method."""
        assert ConfigFile.get_extension_sep() == "."

    def test_get_parent_path(self, my_test_config_file: type[ConfigFile]) -> None:
        """Test method for get_parent_path."""
        expected = Path("parent_dir")
        actual = my_test_config_file.get_parent_path()
        assert_with_msg(actual == expected, f"Expected {expected}, got {actual}")

    def test_load(self, my_test_config_file: type[ConfigFile]) -> None:
        """Test method for load."""
        # assert is dict
        assert_with_msg(
            isinstance(my_test_config_file.load(), dict),
            "Expected dict",
        )

    def test_dump(self, my_test_config_file: type[ConfigFile]) -> None:
        """Test method for dump."""
        # assert dumps correctly
        storage_dict = my_test_config_file.load()
        dunmp_dict = {"key": "value"}
        assert_with_msg(
            storage_dict != dunmp_dict,
            "Expected different dicts",
        )

        my_test_config_file.dump(dunmp_dict)
        assert_with_msg(
            my_test_config_file.load() == dunmp_dict,
            "Expected dump to work",
        )
        # assert raises TypeError if not dict
        with pytest.raises(TypeError):
            my_test_config_file.dump([])

    def test_get_file_extension(self, my_test_config_file: type[ConfigFile]) -> None:
        """Test method for get_file_extension."""
        assert_with_msg(
            my_test_config_file.get_file_extension() == "txt",
            "Expected txt",
        )

    def test_get_configs(self, my_test_config_file: type[ConfigFile]) -> None:
        """Test method for get_configs."""
        assert_with_msg(
            isinstance(my_test_config_file.get_configs(), dict),
            "Expected dict",
        )

    def test___init__(
        self, my_test_config_file: type[ConfigFile], mocker: MockFixture
    ) -> None:
        """Test method for __init__."""
        # create file first to not trigger dunmp in init
        my_test_config_file.get_path().parent.mkdir(parents=True, exist_ok=True)
        # write non-empty file to trigger add_missing_configs,
        # empty file triggers is_unwanted
        my_test_config_file.get_path().write_text("test")
        my_test_config_file()
        after = my_test_config_file.load()

        # assert config is correct
        assert_with_msg(
            after
            == {
                "key0": "value0",
                "key1": "value1",
                "key2": {"key3": "value3"},
                "key4": [
                    ["notvalue4", "extra_value", "value4"],
                    {"key5": "notvalue5", "key6": "value6"},
                ],
                "key7": "value7",
            },
            "Expected config to be correct",
        )

        # remove file to trigger init dump
        my_test_config_file.get_path().unlink()
        my_test_config_file()
        # assert path exists
        assert_with_msg(
            my_test_config_file.get_path().exists(),
            "Expected path to exist",
        )
        # assert config is == get_configs, not any of previous config
        assert_with_msg(
            my_test_config_file.load() == my_test_config_file.get_configs(),
            "Expected config to be correct",
        )

        # mock is_correct to return False
        mocker.patch.object(
            my_test_config_file,
            my_test_config_file.is_correct.__name__,
            return_value=False,
        )
        with pytest.raises(ValueError, match="not correct"):
            my_test_config_file()

    def test_get_path(self, my_test_config_file: type[ConfigFile]) -> None:
        """Test method for get_path."""
        # will be my.txt not my_test.txt bc the fixture factory
        # creates a runtime subclass TestConfigFile so filename will removesuffix
        # see implementation of config_file_factory fixture and get_filename
        expected = Path("parent_dir/my.txt")
        actual = my_test_config_file.get_path()
        # assert actual ends with expected
        assert_with_msg(
            actual.as_posix().endswith(expected.as_posix()),
            f"Expected {expected}, got {actual}",
        )

    def test_get_filename(self, my_test_config_file: type[ConfigFile]) -> None:
        """Test method for get_filename."""
        expected = "my"
        actual = my_test_config_file.get_filename()
        assert_with_msg(actual == expected, f"Expected {expected}, got {actual}")

    def test_add_missing_configs(self, my_test_config_file: type[ConfigFile]) -> None:
        """Test method for add_missing_configs."""
        # same test as in init test
        expected: dict[str, Any] = {
            "key0": "value0",
            "key1": "value1",
            "key2": {"key3": "value3"},
            "key4": [
                ["notvalue4", "extra_value", "value4"],
                {"key5": "notvalue5", "key6": "value6"},
            ],
            "key7": "value7",
        }
        actual = my_test_config_file.add_missing_configs()
        assert_with_msg(actual == expected, "Expected config to be correct")

    def test_add_missing_dict_val(self, my_test_config_file: type[ConfigFile]) -> None:
        """Test method for add_missing_dict_val."""
        expected: dict[str, Any] = {"key": "value"}
        actual: dict[str, Any] = {}
        my_test_config_file.add_missing_dict_val(expected, actual, "key")
        assert_with_msg(
            actual["key"] == expected["key"], "Expected config to be correct"
        )

    def test_insert_missing_list_val(
        self, my_test_config_file: type[ConfigFile]
    ) -> None:
        """Test method for insert_missing_list_val."""
        expected: list[Any] = ["value"]
        actual: list[Any] = []
        my_test_config_file.insert_missing_list_val(expected, actual, 0)
        assert_with_msg(actual[0] == expected[0], "Expected config to be correct")

    def test_is_correct(self, my_test_config_file: type[ConfigFile]) -> None:
        """Test method for is_correct."""
        assert_with_msg(
            not my_test_config_file.is_correct(),
            "Expected config to be correct",
        )
        assert_with_msg(
            my_test_config_file().is_correct(),
            "Expected config to be correct",
        )

    def test_is_unwanted(self, my_test_config_file: type[ConfigFile]) -> None:
        """Test method for is_unwanted."""
        my_test_config_file().get_path().write_text("")
        assert_with_msg(
            my_test_config_file.is_unwanted(),
            "Expected config to be unwanted",
        )

    def test_is_correct_recursively(
        self, my_test_config_file: type[ConfigFile]
    ) -> None:
        """Test method for is_correct_recursively."""
        expected: dict[str, Any] = {
            "key0": "value0",
            "key1": "value1",
            "key2": {"key3": "value3"},
            "key4": [
                ["notvalue4", "extra_value"],
                {"key5": "notvalue5", "key6": "value6"},
            ],
            "key7": "value7",
        }
        actual: dict[str, Any] = {
            "key0": "value0",
            "key1": "value1",
            "key2": {"key3": "value3"},
            "key4": [
                ["notvalue4", "extra_value", "extra_value2"],
                {"key5": "notvalue5", "key6": "value6"},
            ],
            "key7": "value7",
            "key8": "value8",
        }
        assert_with_msg(
            my_test_config_file.is_correct_recursively(expected, actual),
            "Expected config to be correct",
        )
        # change one in actual to not be correct
        actual["key2"]["key3"] = "notvalue3"
        assert_with_msg(
            not my_test_config_file.is_correct_recursively(expected, actual),
            "Expected config to be correct",
        )

    def test_get_all_subclasses(
        self, my_test_config_file: type[ConfigFile], mocker: MockFixture
    ) -> None:
        """Test method for get_all_subclasses."""
        # mock get_all_nonabstract_subclasses to return my_test_config_file
        mocker.patch(
            ConfigFile.__module__
            + "."
            + get_all_nonabst_subcls_from_mod_in_all_deps_depen_on_dep.__name__,
            return_value={my_test_config_file},
        )
        actual = my_test_config_file.get_all_subclasses()
        assert_with_msg(
            my_test_config_file in actual,
            "Expected my_test_config_file to be in actual",
        )
