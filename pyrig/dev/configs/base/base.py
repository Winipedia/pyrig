"""Abstract base classes for configuration file management.

This module provides the ConfigFile abstract base class and format-specific
subclasses for managing project configuration files. The system supports:

    - Automatic discovery of ConfigFile subclasses across dependent packages
    - Subset validation (configs can extend but not contradict base configs)
    - Intelligent merging of missing configuration values
    - Multiple file formats (YAML, TOML, Python, plain text)

The ConfigFile system is the heart of pyrig's automation. When you run
``pyrig init`` or ``pyrig create-root``, all ConfigFile subclasses are
discovered and initialized, creating the complete project configuration.

Subclasses must implement:
    - ``get_parent_path``: Directory containing the config file
    - ``get_file_extension``: File extension (yaml, toml, py, etc.)
    - ``get_configs``: Return the expected configuration structure
    - ``load``: Load configuration from disk
    - ``dump``: Write configuration to disk

Example:
    class MyConfigFile(YamlConfigFile):
        @classmethod
        def get_parent_path(cls) -> Path:
            return Path(".")

        @classmethod
        def get_configs(cls) -> dict[str, Any]:
            return {"key": "value"}
"""

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
    get_module_name_replacing_start_module,
    make_pkg_dir,
    to_path,
)
from pyrig.src.string import split_on_uppercase
from pyrig.src.testing.convention import TESTS_PACKAGE_NAME


class ConfigFile(ABC):
    """Abstract base class for configuration file management.

    Provides automatic creation, validation, and updating of configuration
    files. Subclasses define the file format, location, and expected content.

    The initialization process:
        1. Creates parent directories if needed
        2. Creates the file with default content if it doesn't exist
        3. Validates existing content against expected configuration
        4. Adds any missing configuration values

    Subclasses must implement:
        - ``get_parent_path``: Return the directory for the config file
        - ``get_file_extension``: Return the file extension
        - ``get_configs``: Return the expected configuration structure
        - ``load``: Load and parse the configuration file
        - ``dump``: Write configuration to the file
    """

    @classmethod
    @abstractmethod
    def get_parent_path(cls) -> Path:
        """Get the directory containing the config file.

        Returns:
            Path to the parent directory.
        """

    @classmethod
    @abstractmethod
    def load(cls) -> dict[str, Any] | list[Any]:
        """Load and parse the configuration file.

        Returns:
            The parsed configuration as a dict or list.
        """

    @classmethod
    @abstractmethod
    def dump(cls, config: dict[str, Any] | list[Any]) -> None:
        """Write configuration to the file.

        Args:
            config: The configuration to write.
        """

    @classmethod
    @abstractmethod
    def get_file_extension(cls) -> str:
        """Get the file extension for this config file.

        Returns:
            The file extension without the leading dot.
        """

    @classmethod
    @abstractmethod
    def get_configs(cls) -> dict[str, Any] | list[Any]:
        """Get the expected configuration structure.

        Returns:
            The configuration that should be present in the file.
        """

    def __init__(self) -> None:
        """Initialize the config file, creating or updating as needed.

        Raises:
            ValueError: If the config file cannot be made correct.
        """
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
        """Get the full path to the config file.

        Returns:
            Complete path including filename and extension.
        """
        return cls.get_parent_path() / (
            cls.get_filename() + cls.get_extension_sep() + cls.get_file_extension()
        )

    @classmethod
    def get_extension_sep(cls) -> str:
        """Get the extension separator.

        Returns:
            The string ".".
        """
        return "."

    @classmethod
    def get_filename(cls) -> str:
        """Derive the filename from the class name.

        Removes abstract parent class suffixes and converts to snake_case.

        Returns:
            The filename without extension.
        """
        name = cls.__name__
        abstract_parents = [
            parent.__name__ for parent in cls.__mro__ if inspect.isabstract(parent)
        ]
        for parent in abstract_parents:
            name = name.removesuffix(parent)
        return "_".join(split_on_uppercase(name)).lower()

    @classmethod
    def add_missing_configs(cls) -> dict[str, Any] | list[Any]:
        """Merge expected configuration into the current file.

        Adds any missing keys or values from the expected configuration
        to the current configuration without overwriting existing values.

        Returns:
            The merged configuration.
        """
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
        """Add a missing dictionary value during config merging.

        Args:
            expected_dict: The expected configuration dictionary.
            actual_dict: The actual configuration dictionary to update.
            key: The key to add or update.
        """
        expected_val = expected_dict[key]
        actual_val = actual_dict.get(key)
        actual_dict.setdefault(key, expected_val)

        if isinstance(expected_val, dict) and isinstance(actual_val, dict):
            actual_val.update(expected_val)
        else:
            actual_dict[key] = expected_val

    @staticmethod
    def insert_missing_list_val(
        expected_list: list[Any], actual_list: list[Any], index: int
    ) -> None:
        """Insert a missing list value during config merging.

        Args:
            expected_list: The expected list.
            actual_list: The actual list to update.
            index: The index at which to insert.
        """
        actual_list.insert(index, expected_list[index])

    @classmethod
    def is_correct(cls) -> bool:
        """Check if the configuration file is valid.

        A file is considered correct if:
            - It is empty (user opted out of this config)
            - Its content is a superset of the expected configuration

        Returns:
            True if the configuration is valid.
        """
        return cls.is_unwanted() or cls.is_correct_recursively(
            cls.get_configs(), cls.load()
        )

    @classmethod
    def is_unwanted(cls) -> bool:
        """Check if the user has opted out of this config file.

        An empty file indicates the user doesn't want this configuration.

        Returns:
            True if the file exists and is empty.
        """
        return (
            cls.get_path().exists() and cls.get_path().read_text(encoding="utf-8") == ""
        )

    @staticmethod
    def is_correct_recursively(
        expected_config: dict[str, Any] | list[Any],
        actual_config: dict[str, Any] | list[Any],
    ) -> bool:
        """Recursively check if expected config is a subset of actual.

        Args:
            expected_config: The expected configuration structure.
            actual_config: The actual configuration to validate.

        Returns:
            True if expected is a subset of actual.
        """
        return nested_structure_is_subset(expected_config, actual_config)

    @classmethod
    def get_all_subclasses(cls) -> list[type["ConfigFile"]]:
        """Discover all non-abstract ConfigFile subclasses.

        Searches all packages depending on pyrig for ConfigFile subclasses.

        Returns:
            List of ConfigFile subclass types.
        """
        return get_all_nonabst_subcls_from_mod_in_all_deps_depen_on_dep(
            cls,
            pyrig,
            configs,
            discard_parents=True,
        )

    @classmethod
    def init_config_files(cls) -> None:
        """Initialize all discovered ConfigFile subclasses.

        Initializes files in order: priority files first, then ordered
        files, then all remaining files.
        """
        cls.init_priority_config_files()
        cls.init_ordered_config_files()

        already_inited: set[type[ConfigFile]] = set(
            cls.get_priority_config_files() + cls.get_ordered_config_files()
        )

        subclasses = cls.get_all_subclasses()
        subclasses = [
            subclass for subclass in subclasses if subclass not in already_inited
        ]
        for subclass in subclasses:
            subclass()

    @classmethod
    def get_ordered_config_files(cls) -> list[type["ConfigFile"]]:
        """Get config files that must be initialized in a specific order.

        These files have dependencies on each other and must be
        initialized after priority files but before general files.

        Returns:
            List of ConfigFile types in initialization order.
        """
        from pyrig.dev.configs.testing.conftest import (  # noqa: PLC0415
            ConftestConfigFile,
        )
        from pyrig.dev.configs.testing.fixtures_init import (  # noqa: PLC0415
            FixturesInitConfigFile,
        )

        return [
            FixturesInitConfigFile,
            ConftestConfigFile,
        ]

    @classmethod
    def init_ordered_config_files(cls) -> None:
        """Initialize config files that require specific ordering."""
        for subclass in cls.get_ordered_config_files():
            subclass()

    @classmethod
    def init_priority_config_files(cls) -> None:
        """Initialize high-priority config files first."""
        for subclass in cls.get_priority_config_files():
            subclass()

    @classmethod
    def get_priority_config_files(cls) -> list[type["ConfigFile"]]:
        """Get config files that must be initialized first.

        These files are required by other config files or the build
        process and must exist before other initialization can proceed.

        Returns:
            List of ConfigFile types in priority order.
        """
        # Some must be first:
        from pyrig.dev.configs.git.gitignore import (  # noqa: PLC0415
            GitIgnoreConfigFile,
        )
        from pyrig.dev.configs.licence import (  # noqa: PLC0415
            LicenceConfigFile,
        )
        from pyrig.dev.configs.pyproject import (  # noqa: PLC0415
            PyprojectConfigFile,
        )
        from pyrig.dev.configs.python.builders_init import (  # noqa: PLC0415
            BuildersInitConfigFile,
        )
        from pyrig.dev.configs.python.configs_init import (  # noqa: PLC0415
            ConfigsInitConfigFile,
        )
        from pyrig.dev.configs.python.main import (  # noqa: PLC0415
            MainConfigFile,
        )
        from pyrig.dev.configs.testing.zero_test import (  # noqa: PLC0415
            ZeroTestConfigFile,
        )

        return [
            GitIgnoreConfigFile,
            PyprojectConfigFile,
            LicenceConfigFile,
            MainConfigFile,
            ConfigsInitConfigFile,
            BuildersInitConfigFile,
            ZeroTestConfigFile,
        ]


class YamlConfigFile(ConfigFile):
    """Abstract base class for YAML configuration files.

    Provides YAML-specific load and dump implementations using PyYAML.
    """

    @classmethod
    def load(cls) -> dict[str, Any] | list[Any]:
        """Load and parse the YAML configuration file.

        Returns:
            The parsed YAML content as a dict or list.
        """
        return yaml.safe_load(cls.get_path().read_text(encoding="utf-8")) or {}

    @classmethod
    def dump(cls, config: dict[str, Any] | list[Any]) -> None:
        """Write configuration to the YAML file.

        Args:
            config: The configuration to write.
        """
        with cls.get_path().open("w") as f:
            yaml.safe_dump(config, f, sort_keys=False)

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the YAML file extension.

        Returns:
            The string "yaml".
        """
        return "yaml"


class TomlConfigFile(ConfigFile):
    """Abstract base class for TOML configuration files.

    Provides TOML-specific load and dump implementations using tomlkit,
    which preserves formatting and comments.
    """

    @classmethod
    def load(cls) -> dict[str, Any]:
        """Load and parse the TOML configuration file.

        Returns:
            The parsed TOML content as a dict.
        """
        return tomlkit.parse(cls.get_path().read_text(encoding="utf-8"))

    @classmethod
    def dump(cls, config: dict[str, Any] | list[Any]) -> None:
        """Write configuration to the TOML file.

        Args:
            config: The configuration dict to write.

        Raises:
            TypeError: If config is not a dict.
        """
        if not isinstance(config, dict):
            msg = f"Cannot dump {config} to toml file."
            raise TypeError(msg)
        cls.pretty_dump(config)

    @classmethod
    def prettify_dict(cls, config: dict[str, Any]) -> dict[str, Any]:
        """Convert a dict to a tomlkit table with multiline arrays.

        Args:
            config: The configuration dict to prettify.

        Returns:
            A tomlkit table with formatted arrays.
        """
        t = tomlkit.table()

        for key, value in config.items():
            if isinstance(value, list):
                # Check if all items are dicts - use inline tables for those
                if value and all(isinstance(item, dict) for item in value):
                    arr = tomlkit.array().multiline(multiline=True)
                    for item in value:
                        inline_table = tomlkit.inline_table()
                        inline_table.update(item)
                        arr.append(inline_table)
                    t.add(key, arr)
                else:
                    # For non-dict items, use multiline arrays
                    arr = tomlkit.array().multiline(multiline=True)
                    for item in value:
                        arr.append(item)
                    t.add(key, arr)

            elif isinstance(value, dict):
                t.add(key, cls.prettify_dict(value))

            else:
                t.add(key, value)

        return t

    @classmethod
    def pretty_dump(cls, config: dict[str, Any]) -> None:
        """Write configuration to TOML with pretty formatting.

        Converts lists to multiline arrays for readability.

        Args:
            config: The configuration dict to write.
        """
        # trun all lists into multiline arrays
        config = cls.prettify_dict(config)
        with cls.get_path().open("w") as f:
            tomlkit.dump(config, f, sort_keys=False)

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the TOML file extension.

        Returns:
            The string "toml".
        """
        return "toml"


class TextConfigFile(ConfigFile):
    """Abstract base class for plain text configuration files.

    Suitable for files that have a required starting content but can
    be extended by the user (e.g., Python files, README.md).

    Attributes:
        CONTENT_KEY: Dictionary key used to store file content.
    """

    CONTENT_KEY = "content"

    @classmethod
    @abstractmethod
    def get_content_str(cls) -> str:
        """Get the required content for this file.

        Returns:
            The content string that must be present in the file.
        """

    @classmethod
    def load(cls) -> dict[str, str]:
        """Load the text file content.

        Returns:
            Dict with the file content under CONTENT_KEY.
        """
        return {cls.CONTENT_KEY: cls.get_path().read_text(encoding="utf-8")}

    @classmethod
    def dump(cls, config: dict[str, Any] | list[Any]) -> None:
        """Write content to the text file.

        Appends existing file content to preserve user additions.

        Args:
            config: Dict containing the content to write.

        Raises:
            TypeError: If config is not a dict.
        """
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
        """Get the expected configuration structure.

        Returns:
            Dict with the required content under CONTENT_KEY.
        """
        return {cls.CONTENT_KEY: cls.get_content_str()}

    @classmethod
    def is_correct(cls) -> bool:
        """Check if the text file contains the required content.

        Returns:
            True if the required content is present in the file.
        """
        return (
            super().is_correct()
            or cls.get_content_str().strip() in cls.load()[cls.CONTENT_KEY]
        )

    @classmethod
    def get_file_content(cls) -> str:
        """Get the current file content.

        Returns:
            The full content of the file.
        """
        return cls.load()[cls.CONTENT_KEY]


class MarkdownConfigFile(TextConfigFile):
    """Abstract base class for Markdown configuration files.

    Attributes:
        CONTENT_KEY: Dictionary key used to store file content.
    """

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the Markdown file extension.

        Returns:
            The string "md".
        """
        return "md"


class PythonConfigFile(TextConfigFile):
    """Abstract base class for Python source file configuration.

    Attributes:
        CONTENT_KEY: Dictionary key used to store file content.
    """

    CONTENT_KEY = "content"

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the Python file extension.

        Returns:
            The string "py".
        """
        return "py"


class PythonPackageConfigFile(PythonConfigFile):
    """Abstract base class for Python package configuration files.

    Creates __init__.py files and ensures the parent directory is a
    valid Python package.
    """

    @classmethod
    def dump(cls, config: dict[str, Any] | list[Any]) -> None:
        """Write the config file and ensure parent is a package.

        Args:
            config: The configuration to write.
        """
        super().dump(config)
        make_pkg_dir(cls.get_path().parent)


class CopyModuleConfigFile(PythonPackageConfigFile):
    """Config file that copies content from an existing module.

    Used to replicate pyrig's internal module structure in the target
    project, allowing customization through subclassing.
    """

    @classmethod
    @abstractmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module to copy.

        Returns:
            The module whose content will be copied.
        """

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the target directory for the copied module.

        Transforms the source module path by replacing pyrig with
        the target project's package name.

        Returns:
            Path to the target directory.
        """
        from pyrig.dev.configs.pyproject import PyprojectConfigFile  # noqa: PLC0415

        src_module = cls.get_src_module()
        new_module_name = get_module_name_replacing_start_module(
            src_module, PyprojectConfigFile.get_package_name()
        )
        return to_path(new_module_name, is_package=True).parent

    @classmethod
    def get_content_str(cls) -> str:
        """Get the source module's content as a string.

        Returns:
            The full source code of the module.
        """
        src_module = cls.get_src_module()
        return get_module_content_as_str(src_module)

    @classmethod
    def get_filename(cls) -> str:
        """Get the filename from the source module name.

        Returns:
            The module's isolated name (without package prefix).
        """
        src_module = cls.get_src_module()
        return get_isolated_obj_name(src_module)


class CopyModuleOnlyDocstringConfigFile(CopyModuleConfigFile):
    """Config file that copies only the docstring from a module.

    Useful for creating stub files that preserve documentation
    but allow users to provide their own implementation.
    """

    @classmethod
    def get_content_str(cls) -> str:
        """Extract only the docstring from the source module.

        Returns:
            The module docstring wrapped in triple quotes.
        """
        content = super().get_content_str()
        parts = content.split('"""', 2)
        return '"""' + parts[1] + '"""\n'

    @classmethod
    def is_correct(cls) -> bool:
        """Check if the file contains the source docstring.

        Returns:
            True if the docstring is present in the file.
        """
        docstring = cls.get_content_str().strip()
        # remove the triple quotes from the docstring
        docstring = docstring[3:-3]
        return docstring in cls.get_file_content() or super().is_correct()


class InitConfigFile(CopyModuleOnlyDocstringConfigFile):
    """Config file for creating __init__.py files.

    Copies only the docstring from the source module's __init__.py.
    """

    @classmethod
    def get_filename(cls) -> str:
        """Get the __init__ filename.

        Returns:
            The string "__init__".
        """
        return "__init__"

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the directory where __init__.py will be created.

        Returns:
            Path to the package directory.
        """
        path = super().get_parent_path()
        # this path will be parent of the init file
        return path / get_isolated_obj_name(cls.get_src_module())


class TypedConfigFile(ConfigFile):
    """Config file for py.typed marker files.

    Creates empty py.typed files to indicate PEP 561 compliance.
    """

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the typed file extension.

        Returns:
            The string "typed".
        """
        return "typed"

    @classmethod
    def load(cls) -> dict[str, Any] | list[Any]:
        """Load the py.typed file (always empty).

        Returns:
            An empty dict.
        """
        return {}

    @classmethod
    def dump(cls, config: dict[str, Any] | list[Any]) -> None:
        """Validate that py.typed files remain empty.

        Args:
            config: Must be empty.

        Raises:
            ValueError: If config is not empty.
        """
        if config:
            msg = "Cannot dump to py.typed file."
            raise ValueError(msg)

    @classmethod
    def get_configs(cls) -> dict[str, Any] | list[Any]:
        """Get the expected configuration (empty).

        Returns:
            An empty dict.
        """
        return {}


class PythonTestsConfigFile(PythonConfigFile):
    """Abstract base class for Python files in the tests directory."""

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the tests directory path.

        Returns:
            Path to the tests package.
        """
        return Path(TESTS_PACKAGE_NAME)
