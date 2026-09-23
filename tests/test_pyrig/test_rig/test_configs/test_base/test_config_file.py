"""module."""

import copy
from collections.abc import Callable
from pathlib import Path
from typing import Any, ClassVar

import pytest
from pyrig_env.rig.configs.env import EnvConfigFile
from pytest_mock import MockerFixture

from pyrig.rig import configs
from pyrig.rig.configs.base import config_file
from pyrig.rig.configs.base.config_file import (
    ConfigFile,
    DictConfigFile,
    ListConfigFile,
    validate_config_files,
)
from pyrig.rig.configs.community.license import LicenseConfigFile
from pyrig.rig.configs.package_init import PackageInitConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.configs.readme import ReadmeConfigFile
from pyrig.rig.configs.scratch import ScratchConfigFile


@pytest.fixture
def my_test_config_file(
    config_file_factory: Callable[
        [type[ConfigFile[dict[str, Any]]]],
        type[ConfigFile[dict[str, Any]]],
    ],
) -> type[ConfigFile[dict[str, Any]]]:
    """Create a test config file class with tmp_path."""

    class MyTestConfigFile(config_file_factory(ConfigFile)):  # ty: ignore[unsupported-base]
        """Test config file with tmp_path override."""

        STORAGE_DICT: ClassVar[dict[str, Any]] = {
            "key0": "value0",
            "key1": "value1",
            "key2": {"key3": "value3"},
            "key4": [["value4"], {"key5": "value5", "key6": "value6"}],
        }

        def stem(self) -> str:
            """Get the stem."""
            return "my-test-file"

        def extension(self) -> str:
            """Get the file extension of the config file."""
            return "txt"

        def _load(self) -> dict[str, Any]:
            """Load the config file."""
            return copy.deepcopy(self.STORAGE_DICT)

        def _dump(self, configs: dict[str, Any]) -> None:
            """Dump the config file."""
            self.__class__.STORAGE_DICT = configs

        def parent_path(self) -> Path:
            """Get the path to the config file."""
            return Path("parent_dir")

        def empty_configs(self) -> dict[str, Any]:
            """Get the empty config."""
            return {}

        def _configs(self) -> dict[str, Any]:
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

    def test_filename(
        self,
        my_test_config_file: type[ConfigFile[dict[str, Any]]],
    ) -> None:
        """Test method."""
        assert my_test_config_file().filename() == "my-test-file.txt"

    def test___str__(
        self,
        my_test_config_file: type[ConfigFile[dict[str, Any]]],
    ) -> None:
        """Test method."""
        cf = my_test_config_file()
        assert str(cf.path()) in str(cf)

    def test_version_control_ignored(
        self,
        my_test_config_file: type[ConfigFile[dict[str, Any]]],
    ) -> None:
        """Test method."""
        assert not my_test_config_file().version_control_ignored()

    def test_version_control_ignored_subclasses(self) -> None:
        """Test method."""
        assert set(ConfigFile.version_control_ignored_subclasses()) == {
            ScratchConfigFile,
            EnvConfigFile,
        }

    def test_configs(
        self,
        my_test_config_file: type[ConfigFile[dict[str, Any]]],
    ) -> None:
        """Test method."""
        configs = my_test_config_file()._configs()  # noqa: SLF001
        cached_configs = my_test_config_file().configs()
        assert configs == cached_configs
        assert configs is not cached_configs
        assert my_test_config_file().configs() is cached_configs

    def test_discovery_module(self) -> None:
        """Test method."""
        assert ConfigFile.discovery_module() is configs

    def test_create_file(
        self,
        my_test_config_file: type[ConfigFile[dict[str, Any]]],
    ) -> None:
        """Test method."""
        my_test_config_file().create_file()
        assert my_test_config_file().path().exists()

    def test__load(self, my_test_config_file: type[ConfigFile[dict[str, Any]]]) -> None:
        """Test method."""
        loaded = my_test_config_file()._load()  # noqa: SLF001
        assert loaded["key0"] == "value0"

        # assert cache works
        # _dump to change STORAGE_DICT
        loaded = my_test_config_file().load()
        assert loaded["key0"] == "value0"
        loaded = copy.deepcopy(loaded)
        loaded["key0"] = "new_value0"
        my_test_config_file()._dump(loaded)  # noqa: SLF001
        loaded = my_test_config_file().load()
        assert loaded["key0"] == "value0"  # cache still has old value

        # clear cache and assert new value
        my_test_config_file.load.cache_clear()
        loaded = my_test_config_file().load()
        assert loaded["key0"] == "new_value0"

    def test__dump(self, my_test_config_file: type[ConfigFile[dict[str, Any]]]) -> None:
        """Test method."""
        my_test_config_file()._dump({"key": "value"})  # noqa: SLF001
        assert my_test_config_file().load()["key"] == "value"

        # dump and assert cache is cleared
        my_test_config_file().dump({"key": "new_value"})
        assert my_test_config_file().load()["key"] == "new_value"

    def test_extension_separator(
        self,
        my_test_config_file: type[ConfigFile[dict[str, Any]]],
    ) -> None:
        """Test method."""
        assert my_test_config_file().extension_separator() == "."

    def test_parent_path(
        self,
        my_test_config_file: type[ConfigFile[dict[str, Any]]],
    ) -> None:
        """Test method."""
        expected = Path("parent_dir")
        actual = my_test_config_file().parent_path()
        assert actual == expected, f"Expected {expected}, got {actual}"

    def test_load(self, my_test_config_file: type[ConfigFile[dict[str, Any]]]) -> None:
        """Test method."""
        # assert is dict
        assert isinstance(my_test_config_file().load(), dict), "Expected dict"

    def test_dump(self, my_test_config_file: type[ConfigFile[dict[str, Any]]]) -> None:
        """Test method."""
        # assert dumps correctly
        storage_dict = my_test_config_file().load()
        dump_dict = {"key": "value"}
        assert storage_dict != dump_dict, "Expected different dicts"

        my_test_config_file().dump(dump_dict)
        assert my_test_config_file().load() == dump_dict, "Expected dump to work"

    def test_extension(
        self,
        my_test_config_file: type[ConfigFile[dict[str, Any]]],
    ) -> None:
        """Test method."""
        assert my_test_config_file().extension() == "txt", "Expected txt"

    def test__configs(
        self,
        my_test_config_file: type[ConfigFile[dict[str, Any]]],
    ) -> None:
        """Test method."""
        assert isinstance(my_test_config_file().configs(), dict), "Expected dict"

    def test_validate(
        self,
        my_test_config_file: type[ConfigFile[dict[str, Any]]],
        mocker: MockerFixture,
    ) -> None:
        """Test method."""
        # create file first to not trigger dump in init
        my_test_config_file().path().parent.mkdir(parents=True, exist_ok=True)
        # write non-empty file to trigger merge_configs,
        # empty file triggers is_unwanted
        my_test_config_file().path().write_text("test")
        my_test_config_file().validate()
        after = my_test_config_file().load()

        # assert config is correct
        assert after == {
            "key0": "value0",
            "key1": "value1",
            "key2": {"key3": "value3"},
            "key4": [
                ["value4", "notvalue4", "extra_value"],
                {"key5": "notvalue5", "key6": "value6"},
            ],
            "key7": "value7",
        }

        # remove file to trigger init dump
        my_test_config_file().path().unlink()
        my_test_config_file().validate()
        # assert path exists
        assert my_test_config_file().path().exists(), "Expected path to exist"
        # assert config is == configs, not any of previous config
        assert my_test_config_file().load() == my_test_config_file().configs(), (
            "Expected config to be correct"
        )

        # mock is_correct to return False
        mocker.patch.object(
            my_test_config_file,
            my_test_config_file().is_correct.__name__,
            return_value=False,
        )
        with pytest.raises(
            RuntimeError,
            match=r"failed to validate .*",
        ):
            my_test_config_file().validate()

    def test_validate_reflects_dependency_changes(
        self,
        my_test_config_file: type[ConfigFile[dict[str, Any]]],
        mocker: MockerFixture,
    ) -> None:
        """Test method."""
        # the file itself is already correct, so only whether a dependency
        # needed validation should decide validate()'s return value
        my_test_config_file().dump(my_test_config_file().configs())
        assert my_test_config_file().exists_correct()

        validate_deps_mock = mocker.patch.object(
            config_file,
            validate_config_files.__name__,
            return_value=(),
        )
        assert my_test_config_file().validate() is True
        validate_deps_mock.assert_called_once()

        validate_deps_mock.return_value = (my_test_config_file,)
        assert my_test_config_file().validate() is False

        assert validate_deps_mock.call_count == 2  # noqa: PLR2004

    def test_path(
        self,
        my_test_config_file: type[ConfigFile[dict[str, Any]]],
        tmp_path: Path,
    ) -> None:
        """Test method."""
        assert (
            my_test_config_file().path() == tmp_path / "parent_dir" / "my-test-file.txt"
        )

    def test_stem(self, my_test_config_file: type[ConfigFile[dict[str, Any]]]) -> None:
        """Test method."""
        expected = "my-test-file"
        actual = my_test_config_file().stem()
        assert actual == expected, f"Expected {expected}, got {actual}"

    def test_merge_configs(
        self,
        my_test_config_file: type[ConfigFile[dict[str, Any]]],
    ) -> None:
        """Test method."""
        # same test as in init test
        my_test_config_file().create_file()
        expected: dict[str, Any] = {
            "key0": "value0",
            "key1": "value1",
            "key2": {"key3": "value3"},
            "key4": [
                ["value4", "notvalue4", "extra_value"],
                {"key5": "notvalue5", "key6": "value6"},
            ],
            "key7": "value7",
        }
        actual = my_test_config_file().merge_configs()
        assert actual == expected

    def test_is_correct(
        self,
        my_test_config_file: type[ConfigFile[dict[str, Any]]],
    ) -> None:
        """Test method."""
        assert not my_test_config_file().is_correct()
        my_test_config_file().validate()
        assert my_test_config_file().is_correct()

    def test_removable_subclasses(self) -> None:
        """Test method."""
        expected = set(ConfigFile.concrete_leaves()) - {
            PyprojectConfigFile.L,
        }
        expected_str_reprs = {str(cls.L) for cls in expected}
        actual_str_reprs = {str(cls.L) for cls in ConfigFile.removable_subclasses()}
        assert actual_str_reprs == expected_str_reprs

    def test_removable(self) -> None:
        """Test method."""
        for subclass in ConfigFile.concrete_leaves():
            if subclass is PyprojectConfigFile.L:
                assert not subclass().removable()
                continue
            assert subclass().removable()

    def test_merge_key(self) -> None:
        """Test method."""
        assert PyprojectConfigFile.L.merge_key() == Path("pyproject.toml")
        assert ReadmeConfigFile.L.merge_key() == Path("README.md")

    def test_empty_configs(
        self,
        my_test_config_file: type[ConfigFile[dict[str, Any]]],
    ) -> None:
        """Test method."""
        assert my_test_config_file().empty_configs() == {}

    def test_safe_load(
        self,
        my_test_config_file: type[ConfigFile[dict[str, Any]]],
    ) -> None:
        """Test method."""
        cf = my_test_config_file()
        assert not cf.path().exists()
        assert cf.safe_load() == {}
        cf.create_file()
        cf.dump(cf.configs())
        assert cf.safe_load() == cf.configs()

    def test_leaf_dependencies(self) -> None:
        """Test method."""
        dependencies = tuple(PyprojectConfigFile.I.dependencies())
        assert tuple(PyprojectConfigFile.I.leaf_dependencies()) == tuple(
            dependency.L for dependency in dependencies
        )
        assert len(dependencies) > 0
        assert tuple(LicenseConfigFile.I.leaf_dependencies()) == ()

    def test_dependencies(self) -> None:
        """Test method."""
        assert tuple(PyprojectConfigFile.I.dependencies()) == (
            ReadmeConfigFile,
            LicenseConfigFile,
            PackageInitConfigFile,
        )
        assert LicenseConfigFile.I.dependencies() == ()

    def test_exists_correct(
        self,
        my_test_config_file: type[ConfigFile[dict[str, Any]]],
    ) -> None:
        """Test method."""
        config = my_test_config_file()
        assert not config.exists_correct()

        config.dump(config.configs())
        assert config.exists_correct()


class TestListConfigFile:
    """Test class."""

    def test_empty_configs(self) -> None:
        """Test method."""

        class MyListConfigFile(ListConfigFile):
            def stem(self) -> str:
                return "test"

            def extension(self) -> str:
                return "txt"

            def _load(self) -> list[str]:
                return []

            def _dump(self, configs: list[str]) -> None:
                pass

            def parent_path(self) -> Path:
                return Path()

            def _configs(self) -> list[str]:
                return []

        assert MyListConfigFile().empty_configs() == []


class TestDictConfigFile:
    """Test class."""

    def test_empty_configs(self) -> None:
        """Test method."""

        class MyDictConfigFile(DictConfigFile):
            def stem(self) -> str:
                return "test"

            def extension(self) -> str:
                return "txt"

            def _load(self) -> dict[str, Any]:
                return {}

            def _dump(self, configs: dict[str, Any]) -> None:
                pass

            def parent_path(self) -> Path:
                return Path()

            def _configs(self) -> dict[str, Any]:
                return {}

        assert MyDictConfigFile().empty_configs() == {}


def test_validate_config_files(
    my_test_config_file: type[ConfigFile[dict[str, Any]]],
) -> None:
    """Test function."""
    changed = validate_config_files((my_test_config_file,))
    assert changed == (my_test_config_file,)
    assert my_test_config_file().exists_correct()
