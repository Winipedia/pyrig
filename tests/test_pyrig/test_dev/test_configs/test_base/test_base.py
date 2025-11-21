"""module."""

from collections.abc import Callable
from contextlib import chdir
from pathlib import Path
from types import ModuleType
from typing import Any, ClassVar

import pytest
from pytest_mock import MockFixture

from pyrig.dev.configs.base.base import (
    ConfigFile,
    CopyModuleConfigFile,
    CopyModuleOnlyDocstringConfigFile,
    PythonConfigFile,
    PythonPackageConfigFile,
    PythonTestsConfigFile,
    TextConfigFile,
    TomlConfigFile,
    TypedConfigFile,
    YamlConfigFile,
)
from pyrig.src.modules.class_ import (
    get_all_nonabst_subcls_from_mod_in_all_deps_depen_on_dep,
)
from pyrig.src.testing.assertions import assert_with_msg
from pyrig.src.testing.convention import TESTS_PACKAGE_NAME


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
        def load(cls) -> dict[str, Any] | list[Any]:
            """Load the config file."""
            return cls.STORAGE_DICT

        @classmethod
        def dump(cls, config: dict[str, Any] | list[Any]) -> None:
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

    def test_get_module_name_replacing_start_module(
        self,
        my_test_config_file: type[ConfigFile],
        mocker: MockFixture,
    ) -> None:
        """Test method for get_module_name_replacing_start_module."""
        mock_module = mocker.MagicMock(spec=ModuleType)
        mock_module.__name__ = "pkg1.pkg2.pkg3"

        new_start_module_name = "new_pkg1"
        expected = "new_pkg1.pkg2.pkg3"
        actual = my_test_config_file.get_module_name_replacing_start_module(
            mock_module, new_start_module_name
        )
        assert_with_msg(actual == expected, f"Expected {expected}, got {actual}")

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

    def test_init_config_files(
        self, my_test_config_file: type[ConfigFile], mocker: MockFixture
    ) -> None:
        """Test method for init_config_files."""
        # mock get_all_nonabstract_subclasses to return my_test_config_file
        mocker.patch(
            ConfigFile.__module__
            + "."
            + get_all_nonabst_subcls_from_mod_in_all_deps_depen_on_dep.__name__,
            return_value={my_test_config_file},
        )
        my_test_config_file.init_config_files()
        assert_with_msg(
            my_test_config_file.load() == my_test_config_file.get_configs(),
            "Expected config to be correct",
        )

        tmp_path = Path(
            my_test_config_file.get_path()
            .as_posix()
            .split(my_test_config_file.get_parent_path().as_posix())[0]
        )
        num_created = len(list(tmp_path.rglob("*.*")))
        assert_with_msg(num_created == 1, "Expected other files to be created")


@pytest.fixture
def my_test_yaml_config_file(
    config_file_factory: Callable[[type[YamlConfigFile]], type[YamlConfigFile]],
) -> type[YamlConfigFile]:
    """Create a test yaml config file class with tmp_path."""

    class MyTestYamlConfigFile(config_file_factory(YamlConfigFile)):  # type: ignore [misc]
        """Test yaml config file with tmp_path override."""

        @classmethod
        def get_parent_path(cls) -> Path:
            """Get the path to the config file."""
            return Path()

        @classmethod
        def get_configs(cls) -> dict[str, Any]:
            """Get the config."""
            return {"key": "value"}

    return MyTestYamlConfigFile


class TestYamlConfigFile:
    """Test class."""

    def test_load(self, my_test_yaml_config_file: type[YamlConfigFile]) -> None:
        """Test method for load."""
        my_test_yaml_config_file()
        expected = {"key": "value"}
        actual = my_test_yaml_config_file.load()
        assert_with_msg(actual == expected, f"Expected {expected}, got {actual}")

    def test_dump(self, my_test_yaml_config_file: type[YamlConfigFile]) -> None:
        """Test method for dump."""
        my_test_yaml_config_file.dump({"key": "value"})
        assert_with_msg(
            my_test_yaml_config_file.load() == {"key": "value"},
            "Expected dump to work",
        )

    def test_get_file_extension(
        self, my_test_yaml_config_file: type[YamlConfigFile]
    ) -> None:
        """Test method for get_file_extension."""
        assert_with_msg(
            my_test_yaml_config_file.get_file_extension() == "yaml",
            "Expected yaml",
        )


@pytest.fixture
def my_test_toml_config_file(
    config_file_factory: Callable[[type[TomlConfigFile]], type[TomlConfigFile]],
) -> type[TomlConfigFile]:
    """Create a test toml config file class with tmp_path."""

    class MyTestTomlConfigFile(config_file_factory(TomlConfigFile)):  # type: ignore [misc]
        """Test toml config file with tmp_path override."""

        @classmethod
        def get_parent_path(cls) -> Path:
            """Get the path to the config file."""
            return Path()

        @classmethod
        def get_configs(cls) -> dict[str, Any]:
            """Get the config."""
            return {"key": "value"}

    return MyTestTomlConfigFile


class TestTomlConfigFile:
    """Test class."""

    def test_load(self, my_test_toml_config_file: type[TomlConfigFile]) -> None:
        """Test method for load."""
        my_test_toml_config_file()
        expected = {"key": "value"}
        actual = my_test_toml_config_file.load()
        assert_with_msg(actual == expected, f"Expected {expected}, got {actual}")

    def test_dump(self, my_test_toml_config_file: type[TomlConfigFile]) -> None:
        """Test method for dump."""
        my_test_toml_config_file.dump({"key": "value"})
        assert_with_msg(
            my_test_toml_config_file.load() == {"key": "value"},
            "Expected dump to work",
        )

    def test_get_file_extension(
        self, my_test_toml_config_file: type[TomlConfigFile]
    ) -> None:
        """Test method for get_file_extension."""
        assert_with_msg(
            my_test_toml_config_file.get_file_extension() == "toml",
            "Expected toml",
        )


@pytest.fixture
def my_test_text_config_file(
    config_file_factory: Callable[[type[TextConfigFile]], type[TextConfigFile]],
) -> type[TextConfigFile]:
    """Create a test text config file class with tmp_path."""

    class MyTestTextConfigFile(config_file_factory(TextConfigFile)):  # type: ignore [misc]
        """Test text config file with tmp_path override."""

        @classmethod
        def get_parent_path(cls) -> Path:
            """Get the parent path."""
            return Path()

        @classmethod
        def get_content_str(cls) -> str:
            """Get the content string."""
            return "Test content."

        @classmethod
        def get_file_extension(cls) -> str:
            """Get the file extension."""
            return "txt"

    return MyTestTextConfigFile


class TestTextConfigFile:
    """Test class."""

    def test_get_content_str(
        self, my_test_text_config_file: type[TextConfigFile]
    ) -> None:
        """Test method for get_content_str."""
        content_str = my_test_text_config_file.get_content_str()
        assert_with_msg(
            content_str == "Test content.",
            "Expected 'Test content.'",
        )

    def test_load(self, my_test_text_config_file: type[TextConfigFile]) -> None:
        """Test method for load."""
        my_test_text_config_file()
        loaded = my_test_text_config_file.load()
        assert_with_msg(
            loaded[TextConfigFile.CONTENT_KEY] == "Test content.",
            "Expected 'Test content.'",
        )

    def test_dump(self, my_test_text_config_file: type[TextConfigFile]) -> None:
        """Test method for dump."""
        my_test_text_config_file()
        # Test successful dump
        content = "New content."
        my_test_text_config_file.dump({TextConfigFile.CONTENT_KEY: content})
        loaded = my_test_text_config_file.load()
        assert (
            loaded[TextConfigFile.CONTENT_KEY]
            == content + "\n" + my_test_text_config_file.get_content_str()
        )

    def test_get_configs(self, my_test_text_config_file: type[TextConfigFile]) -> None:
        """Test method for get_configs."""
        configs = my_test_text_config_file.get_configs()
        assert_with_msg(
            configs[TextConfigFile.CONTENT_KEY] == "Test content.",
            "Expected 'Test content.'",
        )

    def test_is_correct(self, my_test_text_config_file: type[TextConfigFile]) -> None:
        """Test method for is_correct."""
        my_test_text_config_file()
        is_correct = my_test_text_config_file.is_correct()
        assert_with_msg(
            is_correct,
            "Expected config to be correct after initialization",
        )

    def test_get_file_content(
        self, my_test_text_config_file: type[TextConfigFile]
    ) -> None:
        """Test method for get_file_content."""
        my_test_text_config_file()
        file_content = my_test_text_config_file.get_file_content()
        assert_with_msg(
            file_content == "Test content.",
            "Expected 'Test content.'",
        )


@pytest.fixture
def my_test_python_config_file(
    config_file_factory: Callable[[type[PythonConfigFile]], type[PythonConfigFile]],
) -> type[PythonConfigFile]:
    """Create a test python config file class with tmp_path."""

    class MyTestPythonConfigFile(config_file_factory(PythonConfigFile)):  # type: ignore [misc]
        """Test python config file with tmp_path override."""

        @classmethod
        def get_parent_path(cls) -> Path:
            """Get the parent path."""
            return Path()

        @classmethod
        def get_content_str(cls) -> str:
            """Get the content string."""
            return '"""Test content."""\n'

    return MyTestPythonConfigFile


class TestPythonConfigFile:
    """Test class."""

    def test_get_file_extension(
        self, my_test_python_config_file: type[PythonConfigFile]
    ) -> None:
        """Test method for get_file_extension."""
        expected = "py"
        actual = my_test_python_config_file.get_file_extension()
        assert_with_msg(actual == expected, f"Expected {expected}, got {actual}")


@pytest.fixture
def my_test_python_tests_config_file(
    config_file_factory: Callable[
        [type[PythonTestsConfigFile]], type[PythonTestsConfigFile]
    ],
) -> type[PythonTestsConfigFile]:
    """Create a test python tests config file class with tmp_path."""

    class MyTestPythonTestsConfigFile(config_file_factory(PythonTestsConfigFile)):  # type: ignore [misc]
        """Test python tests config file with tmp_path override."""

        @classmethod
        def get_content_str(cls) -> str:
            """Get the content string."""
            return '"""Test content."""\n'

    return MyTestPythonTestsConfigFile


class TestPythonTestsConfigFile:
    """Test class."""

    def test_get_parent_path(
        self, my_test_python_tests_config_file: type[PythonTestsConfigFile]
    ) -> None:
        """Test method for get_parent_path."""
        expected = Path(TESTS_PACKAGE_NAME)
        actual = my_test_python_tests_config_file.get_parent_path()
        assert_with_msg(actual == expected, f"Expected {expected}, got {actual}")


@pytest.fixture
def my_test_python_package_config_file(
    config_file_factory: Callable[
        [type[PythonPackageConfigFile]], type[PythonPackageConfigFile]
    ],
    tmp_path: Path,
) -> type[PythonPackageConfigFile]:
    """Create a test python package config file class with tmp_path."""

    class MyTestPythonPackageConfigFile(config_file_factory(PythonPackageConfigFile)):  # type: ignore [misc]
        """Test python package config file with tmp_path override."""

        @classmethod
        def get_parent_path(cls) -> Path:
            """Get the parent path."""
            return Path()

        @classmethod
        def get_content_str(cls) -> str:
            """Get the content string."""
            return '"""Test content."""\n'

        @classmethod
        def dump(cls, config: dict[str, Any] | list[Any]) -> None:
            """Dump the config file."""
            with chdir(tmp_path):
                super().dump(config)

    return MyTestPythonPackageConfigFile


class TestPythonPackageConfigFile:
    """Test class."""

    def test_dump(
        self, my_test_python_package_config_file: type[PythonPackageConfigFile]
    ) -> None:
        """Test method for dump."""
        my_test_python_package_config_file()
        assert_with_msg(
            (
                my_test_python_package_config_file.get_path().parent / "__init__.py"
            ).exists(),
            "Expected __init__.py to be created",
        )


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
        assert_with_msg(actual == expected, f"Expected {expected}, got {actual}")

    def test_load(self, my_test_typed_config_file: type[TypedConfigFile]) -> None:
        """Test method for load."""
        loaded = my_test_typed_config_file.load()
        assert_with_msg(
            loaded == {},
            "Expected load to return empty dict",
        )

    def test_dump(self, my_test_typed_config_file: type[TypedConfigFile]) -> None:
        """Test method for dump."""
        # assert dumps empty dict successfully
        my_test_typed_config_file.dump({})
        assert_with_msg(
            my_test_typed_config_file.load() == {},
            "Expected dump to work with empty dict",
        )
        # assert raises ValueError if config is not empty
        with pytest.raises(ValueError, match=r"Cannot dump to py\.typed file"):
            my_test_typed_config_file.dump({"key": "value"})

    def test_get_configs(
        self, my_test_typed_config_file: type[TypedConfigFile]
    ) -> None:
        """Test method for get_configs."""
        configs = my_test_typed_config_file.get_configs()
        assert_with_msg(
            configs == {},
            "Expected get_configs to return empty dict",
        )


@pytest.fixture
def my_test_copy_module_config_file(
    config_file_factory: Callable[
        [type[PythonPackageConfigFile]], type[PythonPackageConfigFile]
    ],
    tmp_path: Path,
) -> type[PythonPackageConfigFile]:
    """Create a test copy module config file class with tmp_path."""
    # Create a mock module for testing

    mock_module = ModuleType("test_package.test_subpackage.test_module")
    mock_module.__file__ = str(
        tmp_path / "test_package" / "test_subpackage" / "test_module.py"
    )

    # Create the module file with some content
    module_path = Path(mock_module.__file__)
    module_path.parent.mkdir(parents=True, exist_ok=True)
    test_content = (
        '"""Test module content."""\n\n'
        "def test_func():\n"
        '    """Test function."""\n'
        "    pass\n"
    )
    module_path.write_text(test_content)

    class MyTestCopyModuleConfigFile(config_file_factory(CopyModuleConfigFile)):  # type: ignore [misc]
        """Test copy module config file with tmp_path override."""

        @classmethod
        def get_src_module(cls) -> ModuleType:
            """Get the source module."""
            return mock_module

        @classmethod
        def dump(cls, config: dict[str, Any] | list[Any]) -> None:
            """Dump the config file."""
            with chdir(tmp_path):
                super().dump(config)

    return MyTestCopyModuleConfigFile


class TestCopyModuleConfigFile:
    """Test class."""

    def test_get_src_module(
        self, my_test_copy_module_config_file: type[CopyModuleConfigFile]
    ) -> None:
        """Test method for get_src_module."""
        src_module = my_test_copy_module_config_file.get_src_module()
        assert_with_msg(
            isinstance(src_module, ModuleType),
            "Expected ModuleType",
        )
        expected_name = "test_package.test_subpackage.test_module"
        assert_with_msg(
            src_module.__name__ == expected_name,
            f"Expected '{expected_name}', got {src_module.__name__}",
        )

    def test_get_parent_path(
        self, my_test_copy_module_config_file: type[CopyModuleConfigFile]
    ) -> None:
        """Test method for get_parent_path."""
        parent_path = my_test_copy_module_config_file.get_parent_path()
        assert_with_msg(
            isinstance(parent_path, Path),
            "Expected Path",
        )

    def test_get_content_str(
        self, my_test_copy_module_config_file: type[CopyModuleConfigFile]
    ) -> None:
        """Test method for get_content_str."""
        content_str = my_test_copy_module_config_file.get_content_str()
        assert_with_msg(
            len(content_str) > 0,
            "Expected non-empty string",
        )
        # Verify it contains the module content
        assert_with_msg(
            "Test module content" in content_str,
            "Expected module content in string",
        )

    def test_get_filename(
        self, my_test_copy_module_config_file: type[CopyModuleConfigFile]
    ) -> None:
        """Test method for get_filename."""
        filename = my_test_copy_module_config_file.get_filename()
        assert_with_msg(
            filename == "test_module",
            f"Expected 'test_module', got {filename}",
        )


@pytest.fixture
def my_test_copy_module_only_docstring_config_file(
    my_test_copy_module_config_file: type[CopyModuleConfigFile],
) -> type[CopyModuleOnlyDocstringConfigFile]:
    """Create a test copy module only docstring config file class with tmp_path."""

    class MyTestCopyModuleOnlyDocstringConfigFile(
        CopyModuleOnlyDocstringConfigFile,
        my_test_copy_module_config_file,  # type: ignore [misc, valid-type]
    ):
        """Test copy module only docstring config file with tmp_path override."""

    return MyTestCopyModuleOnlyDocstringConfigFile


class TestCopyModuleOnlyDocstringConfigFile:
    """Test class."""

    def test_get_content_str(
        self,
        my_test_copy_module_only_docstring_config_file: type[
            CopyModuleOnlyDocstringConfigFile
        ],
    ) -> None:
        """Test method."""
        content_str = my_test_copy_module_only_docstring_config_file.get_content_str()

        # assert its only the docstring
        assert content_str == '"""Test module content."""\n', (
            "Expected only docstring in string"
        )
