"""Base class for config files."""

import inspect
from abc import ABC, abstractmethod
from pathlib import Path
from types import ModuleType
from typing import Any

import tomlkit
import yaml

import pyrig
from pyrig.dev import configs
from pyrig.src.iterate import nested_structure_is_subset
from pyrig.src.modules.class_ import (
    get_all_nonabst_subcls_from_mod_in_all_deps_depen_on_dep,
)
from pyrig.src.modules.module import (
    get_isolated_obj_name,
    get_module_content_as_str,
    make_pkg_dir,
    to_path,
)
from pyrig.src.string import split_on_uppercase
from pyrig.src.testing.convention import TESTS_PACKAGE_NAME


class ConfigFile(ABC):
    """Base class for config files."""

    @classmethod
    @abstractmethod
    def get_parent_path(cls) -> Path:
        """Get the path to the config file."""

    @classmethod
    @abstractmethod
    def load(cls) -> dict[str, Any] | list[Any]:
        """Load the config file."""

    @classmethod
    @abstractmethod
    def dump(cls, config: dict[str, Any] | list[Any]) -> None:
        """Dump the config file."""

    @classmethod
    @abstractmethod
    def get_file_extension(cls) -> str:
        """Get the file extension of the config file."""

    @classmethod
    @abstractmethod
    def get_configs(cls) -> dict[str, Any] | list[Any]:
        """Get the config."""

    def __init__(self) -> None:
        """Initialize the config file."""
        self.get_path().parent.mkdir(parents=True, exist_ok=True)
        if not self.get_path().exists():
            self.get_path().touch()
            self.dump(self.get_configs())

        if not self.is_correct():
            config = self.add_missing_configs()
            self.dump(config)

        if not self.is_correct():
            msg = f"Config file {self.get_path()} is not correct."
            raise ValueError(msg)

    @classmethod
    def get_path(cls) -> Path:
        """Get the path to the config file."""
        return (
            cls.get_parent_path() / f"{cls.get_filename()}.{cls.get_file_extension()}"
        )

    @classmethod
    def get_filename(cls) -> str:
        """Get the filename of the config file."""
        name = cls.__name__
        abstract_parents = [
            parent.__name__ for parent in cls.__mro__ if inspect.isabstract(parent)
        ]
        for parent in abstract_parents:
            name = name.removesuffix(parent)
        return "_".join(split_on_uppercase(name)).lower()

    @classmethod
    def add_missing_configs(cls) -> dict[str, Any] | list[Any]:
        """Add any missing configs to the config file."""
        current_config = cls.load()
        expected_config = cls.get_configs()
        nested_structure_is_subset(
            expected_config,
            current_config,
            cls.add_missing_dict_val,
            cls.insert_missing_list_val,
        )
        return current_config

    @staticmethod
    def add_missing_dict_val(
        expected_dict: dict[str, Any], actual_dict: dict[str, Any], key: str
    ) -> None:
        """Add a missing dict value."""
        actual_dict[key] = expected_dict[key]

    @staticmethod
    def insert_missing_list_val(
        expected_list: list[Any], actual_list: list[Any], index: int
    ) -> None:
        """Append a missing list value."""
        actual_list.insert(index, expected_list[index])

    @classmethod
    def is_correct(cls) -> bool:
        """Check if the config is correct.

        If the file is empty, it is considered correct.
        This is so bc if a user does not want a specific config file,
        they can just make it empty and the tests will not fail.
        """
        return cls.is_unwanted() or cls.is_correct_recursively(
            cls.get_configs(), cls.load()
        )

    @classmethod
    def is_unwanted(cls) -> bool:
        """Check if the config file is unwanted.

        If the file is empty, it is considered unwanted.
        """
        return (
            cls.get_path().exists() and cls.get_path().read_text(encoding="utf-8") == ""
        )

    @staticmethod
    def is_correct_recursively(
        expected_config: dict[str, Any] | list[Any],
        actual_config: dict[str, Any] | list[Any],
    ) -> bool:
        """Check if the config is correct.

        Checks if expected is a subset recursively of actual.
        If a value is Any, it is considered correct.

        Args:
            expected_config: The expected config
            actual_config: The actual config

        Returns:
            True if the config is correct, False otherwise
        """
        return nested_structure_is_subset(expected_config, actual_config)

    @classmethod
    def get_all_subclasses(cls) -> list[type["ConfigFile"]]:
        """Get all subclasses of ConfigFile."""
        return get_all_nonabst_subcls_from_mod_in_all_deps_depen_on_dep(
            cls, pyrig, configs
        )

    @classmethod
    def init_config_files(cls) -> None:
        """Initialize all subclasses."""
        # Some must be first:
        from pyrig.dev.configs.git.gitignore import (  # noqa: PLC0415
            GitIgnoreConfigFile,
        )
        from pyrig.dev.configs.pyproject import (  # noqa: PLC0415
            PyprojectConfigFile,
        )
        from pyrig.dev.configs.python.builder import (  # noqa: PLC0415
            BuilderConfigFile,
        )
        from pyrig.dev.configs.python.configs import (  # noqa: PLC0415
            ConfigsConfigFile,
        )
        from pyrig.dev.configs.python.src_init import (  # noqa: PLC0415
            SrcInitConfigFile,
        )
        from pyrig.dev.configs.testing.conftest import (  # noqa: PLC0415
            ConftestConfigFile,
        )

        priorities: list[type[ConfigFile]] = [
            GitIgnoreConfigFile,
            PyprojectConfigFile,
            SrcInitConfigFile,
            ConfigsConfigFile,
            BuilderConfigFile,
            ConftestConfigFile,
        ]
        for subclass in priorities:
            subclass()

        subclasses = cls.get_all_subclasses()
        subclasses = [subclass for subclass in subclasses if subclass not in priorities]
        for subclass in subclasses:
            subclass()

    @classmethod
    def get_module_name_replacing_start_module(
        cls, module: ModuleType, new_start_module_name: str
    ) -> str:
        """Get the module name of a module replacing the start module."""
        module_current_start = module.__name__.split(".")[0]
        return module.__name__.replace(module_current_start, new_start_module_name, 1)


class YamlConfigFile(ConfigFile):
    """Base class for yaml config files."""

    @classmethod
    def load(cls) -> dict[str, Any] | list[Any]:
        """Load the config file."""
        return yaml.safe_load(cls.get_path().read_text(encoding="utf-8")) or {}

    @classmethod
    def dump(cls, config: dict[str, Any] | list[Any]) -> None:
        """Dump the config file."""
        with cls.get_path().open("w") as f:
            yaml.safe_dump(config, f, sort_keys=False)

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the file extension of the config file."""
        return "yaml"


class TomlConfigFile(ConfigFile):
    """Base class for toml config files."""

    @classmethod
    def load(cls) -> dict[str, Any]:
        """Load the config file."""
        return tomlkit.parse(cls.get_path().read_text(encoding="utf-8"))

    @classmethod
    def dump(cls, config: dict[str, Any] | list[Any]) -> None:
        """Dump the config file."""
        if not isinstance(config, dict):
            msg = f"Cannot dump {config} to toml file."
            raise TypeError(msg)
        with cls.get_path().open("w") as f:
            tomlkit.dump(config, f, sort_keys=False)

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the file extension of the config file."""
        return "toml"


class TextConfigFile(ConfigFile):
    """Base class for text config files.

    Those files just have a starting text
    and then can be added to. Like python files or README.md
    """

    CONTENT_KEY = "content"

    @classmethod
    @abstractmethod
    def get_content_str(cls) -> str:
        """Get the content."""

    @classmethod
    def load(cls) -> dict[str, str]:
        """Load the config file."""
        return {cls.CONTENT_KEY: cls.get_path().read_text(encoding="utf-8")}

    @classmethod
    def dump(cls, config: dict[str, Any] | list[Any]) -> None:
        """Dump the config file."""
        if not isinstance(config, dict):
            msg = f"Cannot dump {config} to text file."
            raise TypeError(msg)
        if cls.get_file_content().strip():
            config[cls.CONTENT_KEY] = (
                config[cls.CONTENT_KEY] + "\n" + cls.get_file_content()
            )
        cls.get_path().write_text(config[cls.CONTENT_KEY], encoding="utf-8")

    @classmethod
    def get_configs(cls) -> dict[str, Any]:
        """Get the config."""
        return {cls.CONTENT_KEY: cls.get_content_str()}

    @classmethod
    def is_correct(cls) -> bool:
        """Check if the config is correct.

        Text files are correct if they exist and contain the correct content.
        """
        return (
            super().is_correct()
            or cls.get_content_str().strip() in cls.load()[cls.CONTENT_KEY]
        )

    @classmethod
    def get_file_content(cls) -> str:
        """Get the file content."""
        return cls.load()[cls.CONTENT_KEY]


class PythonConfigFile(TextConfigFile):
    """Base class for python config files."""

    CONTENT_KEY = "content"

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the file extension of the config file."""
        return "py"


class PythonPackageConfigFile(PythonConfigFile):
    """Base class for python package config files.

    They create an init file.
    """

    @classmethod
    def dump(cls, config: dict[str, Any] | list[Any]) -> None:
        """Dump the config file."""
        super().dump(config)
        make_pkg_dir(cls.get_path().parent)


class CopyModuleConfigFile(PythonPackageConfigFile):
    """Config file that copies a module."""

    @classmethod
    @abstractmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module."""

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the path to the config file.

        Replaces the start module with the package name.
        """
        from pyrig.dev.configs.pyproject import PyprojectConfigFile  # noqa: PLC0415

        src_module = cls.get_src_module()
        new_module_name = cls.get_module_name_replacing_start_module(
            src_module, PyprojectConfigFile.get_package_name()
        )
        return to_path(new_module_name, is_package=True).parent

    @classmethod
    def get_content_str(cls) -> str:
        """Get the content."""
        src_module = cls.get_src_module()
        return get_module_content_as_str(src_module)

    @classmethod
    def get_filename(cls) -> str:
        """Get the filename of the config file."""
        src_module = cls.get_src_module()
        return get_isolated_obj_name(src_module)


class TypedConfigFile(ConfigFile):
    """Config file for py.typed."""

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the file extension of the config file."""
        return "typed"

    @classmethod
    def load(cls) -> dict[str, Any] | list[Any]:
        """Load the config file."""
        return {}

    @classmethod
    def dump(cls, config: dict[str, Any] | list[Any]) -> None:
        """Dump the config file."""
        if config:
            msg = "Cannot dump to py.typed file."
            raise ValueError(msg)

    @classmethod
    def get_configs(cls) -> dict[str, Any] | list[Any]:
        """Get the config."""
        return {}


class PythonTestsConfigFile(PythonConfigFile):
    """Base class for python config files in the tests directory."""

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the path to the config file."""
        return Path(TESTS_PACKAGE_NAME)
