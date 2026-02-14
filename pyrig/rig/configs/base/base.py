"""Abstract base class for declarative configuration file management.

Provides ConfigFile for automated config management with automatic discovery,
subset validation, intelligent merging, priority-based validation, and
parallel execution.

Subclass Requirements:
    Must implement:
    - `parent_path()`: Directory containing the file
    - `extension()`: File extension without leading dot
    - `_configs()`: Expected configuration structure (internal implementation)
    - `_load()`: Load and parse the file (internal implementation)
    - `_dump(config)`: Write configuration to file (internal implementation)

    Optionally override:
    - `priority()`: Float priority (default 0, higher = first)
    - `filename()`: Filename without extension (auto-derived from class name)

    Public API (already implemented, do not override):
    - `configs()`: Cached wrapper around `_configs()`
    - `load()`: Cached wrapper around `_load()`
    - `dump(config)`: Cache-invalidating wrapper around `_dump(config)`

Example:
    Create a custom TOML config file::

        from pathlib import Path
        from typing import Any
        from pyrig.rig.configs.base.toml import TomlConfigFile

        class MyAppConfigFile(TomlConfigFile):
            '''Manages myapp.toml configuration.'''

            @classmethod
            def parent_path(cls) -> Path:
                '''Place in project root.'''
                return Path()

            @classmethod
            def _configs(cls) -> dict[str, Any]:
                '''Define expected configuration.'''
                return {
                    "app": {
                        "name": "myapp",
                        "version": "1.0.0"
                    }
                }

            @classmethod
            def priority(cls) -> float:
                '''Validate after pyproject.toml.'''
                return 50

    The system will automatically:
    - Create `myapp.toml` if it doesn't exist
    - Add missing keys if file exists but incomplete
    - Preserve any extra keys user added
    - Validate final result matches expected structure

See Also:
    pyrig.rig.configs: Package-level documentation
    pyrig.src.iterate.nested_structure_is_subset: Subset validation logic
    pyrig.src.modules.package.discover_subclasses_across_dependents:
        Subclass discovery mechanism
"""

import inspect
import logging
from abc import abstractmethod
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from functools import cache
from pathlib import Path
from types import ModuleType
from typing import Any, Self

from pyrig.rig import configs
from pyrig.src.iterate import nested_structure_is_subset
from pyrig.src.string_ import split_on_uppercase
from pyrig.src.subclass import SingletonDependencySubclass

logger = logging.getLogger(__name__)


class Priority:
    """Priority levels for config file validation ordering."""

    DEFAULT = 0
    LOW = DEFAULT + 10
    MEDIUM = LOW + 10
    HIGH = MEDIUM + 10


class ConfigFile[ConfigT: dict[str, Any] | list[Any]](SingletonDependencySubclass):
    """Abstract base class for declarative configuration file management.

    Declarative, idempotent system for managing config files. Preserves user
    customizations while ensuring required configuration is present.

    Type Parameters:
        ConfigT: The configuration type (dict[str, Any] or list[Any]).

    Subclass Requirements:
        Must implement (internal methods with underscore prefix):
        - `parent_path()`: Directory containing the file
        - `extension()`: File extension (e.g., "toml", "yaml")
        - `_configs()`: Expected configuration (dict or list) - internal
        - `_load()`: Load and parse the file - internal implementation
        - `_dump(config)`: Write configuration to file - internal implementation

        Optionally override:
        - `priority()`: validation priority (default 0)
        - `filename()`: Filename without extension (auto-derived)

        Public API (already implemented with caching, do not override):
        - `configs()`: Returns cached result of `_configs()`
        - `load()`: Returns cached result of `_load()`
        - `dump(config)`: Invalidates cache and calls `_dump(config)`

    See Also:
        pyrig.rig.configs: Package-level documentation
        pyrig.rig.configs.base.toml.TomlConfigFile: TOML file base class
        pyrig.rig.configs.base.yaml.YamlConfigFile: YAML file base class
        pyrig.src.iterate.nested_structure_is_subset: Subset validation
    """

    @classmethod
    @abstractmethod
    def parent_path(cls) -> Path:
        """Return directory containing the config file.

        Returns:
            Path to parent directory, relative to project root.
        """

    @classmethod
    @abstractmethod
    def _load(cls) -> ConfigT:
        """Load and parse configuration file.

        Returns:
            Parsed configuration as dict or list. Implementations should return
            empty dict/list for empty files to support opt-out behavior.
        """

    @classmethod
    @abstractmethod
    def _dump(cls, config: ConfigT) -> None:
        """Write configuration to file.

        Args:
            config: Configuration to write (dict or list).
        """

    @classmethod
    @abstractmethod
    def extension(cls) -> str:
        """Return file extension without leading dot.

        Returns:
            File extension (e.g., "toml", "yaml", "json", "py", "md").
        """

    @classmethod
    @abstractmethod
    def _configs(cls) -> ConfigT:
        """Return expected configuration structure.

        Returns:
            Minimum required configuration as dict or list.
        """

    @classmethod
    def definition_package(cls) -> ModuleType:
        """Return the package containing ConfigFile subclass definitions.

        Default is `pyrig.rig.configs`. Can be overridden by subclasses to
        define their own package.

        Returns:
            Package module where ConfigFile subclasses are defined.
        """
        return configs

    @classmethod
    def sorting_key(cls, subclass: type[Self]) -> float:
        """Return a numeric sort key for the given config-file subclass.

        Subclasses may define priorities via `priority()`. This method
        returns a value that can be used to sort subclasses so that higher
        priority subclasses appear earlier. Implementations should return a
        float where a smaller value sorts earlier when used with Python's
        ascending sort; this base implementation returns the negative of the
        subclass priority so that higher priority sorts first.

        Args:
            subclass (type[Self]): The subclass to compute a key for.

        Returns:
            float: A numeric key suitable for sorting subclasses.
        """
        # sort by priority (higher first),
        # so return negative priority for ascending sort
        return -subclass.priority()

    @staticmethod
    def validate_config_file(
        config_file_cls: type["ConfigFile[ConfigT]"],
    ) -> None:
        """Validate a single config file class.

        Args:
            config_file_cls: The ConfigFile subclass to validate.
        """
        config_file_cls.validate()

    @classmethod
    def validate(cls) -> None:
        """Validate config file, creating or updating as needed.

        Calls create_file() if file doesn't exist (which creates parent dirs and file),
        validates content, and adds missing configs if needed.
        Idempotent and preserves user customizations.

        Raises:
            ValueError: If file cannot be made correct.
        """
        path = cls.path()
        logger.debug(
            "Validating config file: %s at: %s",
            cls.__name__,
            path,
        )
        if not path.exists():
            cls.create_file()
            cls.dump(cls.configs())

        if not cls.is_correct():
            config = cls.merge_configs()
            cls.dump(config)

        if not cls.is_correct():
            msg = f"Config file {path} is not correct after adding missing configs."
            raise ValueError(msg)

    @classmethod
    def create_file(cls) -> None:
        """Create the config file and its parent directories."""
        path = cls.path()
        logger.info("Creating config file %s at: %s", cls.__name__, path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()

    @classmethod
    @cache
    def configs(cls) -> ConfigT:
        """Return expected configuration structure.

        Cached to avoid multiple calls to _configs().

        Returns:
            Minimum required configuration as dict or list.
        """
        return cls._configs()

    @classmethod
    @cache
    def load(cls) -> ConfigT:
        """Load and parse configuration file.

        Cached to avoid multiple reads of same file.

        Returns:
            Parsed configuration as dict or list. Format-specific implementations
            typically return empty dict/list for empty files (opt-out behavior).
        """
        logger.debug("Loading config file %s", cls.__name__)
        return cls._load()

    @classmethod
    def dump(cls, config: ConfigT) -> None:
        """Write configuration to file.

        Clears the cache before writing to ensure the dump operation reads
        the current file state if it loads, and after writing to ensure subsequent loads
        reflect the latest state.

        Args:
            config: Configuration to write (dict or list).
        """
        logger.info("Updating config file %s at: %s", cls.__name__, cls.path())
        cls.load.cache_clear()
        cls._dump(config)
        cls.load.cache_clear()

    @classmethod
    def priority(cls) -> float:
        """Return validation priority (higher = first, default 0)."""
        return Priority.DEFAULT

    @classmethod
    def path(cls) -> Path:
        """Return full path by combining parent path, filename, and extension."""
        return cls.parent_path() / (
            cls.filename() + cls.extension_separator() + cls.extension()
        )

    @classmethod
    def extension_separator(cls) -> str:
        """Return extension separator character (always ".")."""
        return "."

    @classmethod
    def filename(cls) -> str:
        """Derive filename from class name (auto-converts to snake_case).

        Returns:
            Filename without extension.
        """
        name = cls.__name__
        abstract_parents = [
            parent.__name__ for parent in cls.__mro__ if inspect.isabstract(parent)
        ]
        for parent in abstract_parents:
            name = name.removesuffix(parent)
        return "_".join(split_on_uppercase(name)).lower()

    @classmethod
    def merge_configs(cls) -> ConfigT:
        """Merge expected config into current, preserving user customizations.

        Returns:
            Merged configuration with all expected values and user additions.

        See Also:
            pyrig.src.iterate.nested_structure_is_subset: Subset validation logic
        """
        current_config = cls.load()
        expected_config = cls.configs()
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
        """Merge dict value during config merging (modifies actual_dict in place).

        First calls setdefault to add key if missing. Then:
        - For dict values: updates actual with expected (overwrites overlapping
          keys with expected values, preserves actual-only keys, adds
          expected-only keys)
        - For non-dict values: replaces actual value with expected value

        Args:
            expected_dict: Expected configuration dict.
            actual_dict: Actual configuration dict to update.
            key: Key to add or update.
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
        """Insert missing list value during config merging (modifies in place).

        Args:
            expected_list: Expected list.
            actual_list: Actual list to update.
            index: Index at which to insert.
        """
        actual_list.insert(index, expected_list[index])

    @classmethod
    def is_correct(cls) -> bool:
        """Check if config file is valid (empty or expected is subset of actual).

        Returns:
            True if valid (opted out or contains all expected configuration).

        See Also:
            is_unwanted: Check if user opted out
            is_correct_recursively: Perform subset validation
        """
        return cls.path().exists() and (
            cls.is_unwanted() or cls.is_correct_recursively(cls.configs(), cls.load())
        )

    @classmethod
    def is_unwanted(cls) -> bool:
        """Check if user opted out (file exists and is empty).

        Returns:
            True if file exists and is completely empty.
        """
        return cls.path().exists() and cls.path().stat().st_size == 0

    @staticmethod
    def is_correct_recursively(
        expected_config: ConfigT,
        actual_config: ConfigT,
    ) -> bool:
        """Recursively check if expected config is subset of actual.

        Args:
            expected_config: Expected configuration structure.
            actual_config: Actual configuration to validate.

        Returns:
            True if expected is subset of actual.

        See Also:
            pyrig.src.iterate.nested_structure_is_subset: Core subset logic
        """
        return nested_structure_is_subset(expected_config, actual_config)

    @classmethod
    def priority_subclasses(cls) -> list[type[Self]]:
        """Get ConfigFile subclasses with priority > 0.

        Returns:
            List of ConfigFile subclass types with priority > 0 (highest first).

        See Also:
            subclasses: Get all subclasses regardless of priority
            validate_priority_subclasses: validate only priority subclasses
        """
        return [cf for cf in cls.subclasses() if cf.priority() > 0]

    @classmethod
    def validate_subclasses(
        cls,
        *subclasses: type[Self],
    ) -> None:
        """Validate specific ConfigFile subclasses with priority-based ordering.

        Group by priority, validate in the given order, parallel within groups.

        Args:
            subclasses: ConfigFile subclasses to validate.

        See Also:
            validate_all_subclasses: validate all discovered subclasses
            validate_priority_subclasses: validate only priority subclasses
        """
        # order by priority
        subclasses_by_priority: dict[float, list[type[ConfigFile[Any]]]] = defaultdict(
            list
        )
        for cf in subclasses:
            subclasses_by_priority[cf.priority()].append(cf)

        biggest_group = (
            max(subclasses_by_priority.values(), key=len)
            if subclasses_by_priority
            else []
        )
        max_workers = len(biggest_group) or 1
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for priority in sorted(subclasses_by_priority.keys(), reverse=True):
                cf_group = subclasses_by_priority[priority]
                logger.debug(
                    "Validating %d config files with priority: %s",
                    len(cf_group),
                    priority,
                )
                list(executor.map(cls.validate_config_file, cf_group))

    @classmethod
    def validate_all_subclasses(cls) -> None:
        """Validate all discovered ConfigFile subclasses in priority order.

        See Also:
            subclasses: Discovery mechanism
            validate_subclasses: validation mechanism
            validate_priority_subclasses: validate only priority files
        """
        logger.info("Creating all config files")
        cls.validate_subclasses(*cls.subclasses())

    @classmethod
    def validate_priority_subclasses(cls) -> None:
        """Validate only ConfigFile subclasses with priority > 0.

        See Also:
            priority_subclasses: Discovery mechanism
            validate_subclasses: validation mechanism
            validate_all_subclasses: validate all files
        """
        logger.info("Creating priority config files")
        cls.validate_subclasses(*cls.priority_subclasses())
