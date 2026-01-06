"""Abstract base class for declarative configuration file management.

Provides ConfigFile for automated config management with automatic discovery,
subset validation, intelligent merging, priority-based initialization, and
parallel execution.

Subclass Requirements:
    Must implement:
    - `get_parent_path()`: Directory containing the file
    - `get_file_extension()`: File extension without leading dot
    - `_get_configs()`: Expected configuration structure (internal implementation)
    - `_load()`: Load and parse the file (internal implementation)
    - `_dump(config)`: Write configuration to file (internal implementation)

    Optionally override:
    - `get_priority()`: Float priority (default 0, higher = first)
    - `get_filename()`: Filename without extension (auto-derived from class name)

    Public API (already implemented, do not override):
    - `get_configs()`: Cached wrapper around `_get_configs()`
    - `load()`: Cached wrapper around `_load()`
    - `dump(config)`: Cache-invalidating wrapper around `_dump(config)`

Example:
    Create a custom TOML config file::

        from pathlib import Path
        from typing import Any
        from pyrig.dev.configs.base.toml import TomlConfigFile

        class MyAppConfigFile(TomlConfigFile):
            '''Manages myapp.toml configuration.'''

            @classmethod
            def get_parent_path(cls) -> Path:
                '''Place in project root.'''
                return Path()

            @classmethod
            def _get_configs(cls) -> dict[str, Any]:
                '''Define expected configuration.'''
                return {
                    "app": {
                        "name": "myapp",
                        "version": "1.0.0"
                    }
                }

            @classmethod
            def get_priority(cls) -> float:
                '''Initialize after pyproject.toml.'''
                return 50

    The system will automatically:
    - Create `myapp.toml` if it doesn't exist
    - Add missing keys if file exists but incomplete
    - Preserve any extra keys user added
    - Validate final result matches expected structure

See Also:
    pyrig.dev.configs: Package-level documentation
    pyrig.src.iterate.nested_structure_is_subset: Subset validation logic
    pyrig.src.modules.package.discover_subclasses_across_dependents:
        Subclass discovery mechanism
"""

import inspect
import logging
from abc import ABC, abstractmethod
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from functools import cache
from pathlib import Path
from types import ModuleType
from typing import Any, Self

import pyrig
from pyrig.dev import configs
from pyrig.src.iterate import nested_structure_is_subset
from pyrig.src.modules.class_ import classproperty
from pyrig.src.modules.package import (
    discover_leaf_subclass_across_dependents,
    discover_subclasses_across_dependents,
)
from pyrig.src.string_ import split_on_uppercase

logger = logging.getLogger(__name__)


class ConfigFile[ConfigT: dict[str, Any] | list[Any]](ABC):
    """Abstract base class for declarative configuration file management.

    Declarative, idempotent system for managing config files. Preserves user
    customizations while ensuring required configuration is present.

    Type Parameters:
        ConfigT: The configuration type (dict[str, Any] or list[Any]).

    Subclass Requirements:
        Must implement (internal methods with underscore prefix):
        - `get_parent_path()`: Directory containing the file
        - `get_file_extension()`: File extension (e.g., "toml", "yaml")
        - `_get_configs()`: Expected configuration (dict or list) - internal
        - `_load()`: Load and parse the file - internal implementation
        - `_dump(config)`: Write configuration to file - internal implementation

        Optionally override:
        - `get_priority()`: Initialization priority (default 0)
        - `get_filename()`: Filename without extension (auto-derived)

        Public API (already implemented with caching, do not override):
        - `get_configs()`: Returns cached result of `_get_configs()`
        - `load()`: Returns cached result of `_load()`
        - `dump(config)`: Invalidates cache and calls `_dump(config)`

    See Also:
        pyrig.dev.configs: Package-level documentation
        pyrig.dev.configs.base.toml.TomlConfigFile: TOML file base class
        pyrig.dev.configs.base.yaml.YamlConfigFile: YAML file base class
        pyrig.src.iterate.nested_structure_is_subset: Subset validation
    """

    @classmethod
    @abstractmethod
    def get_parent_path(cls) -> Path:
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
    def get_file_extension(cls) -> str:
        """Return file extension without leading dot.

        Returns:
            File extension (e.g., "toml", "yaml", "json", "py", "md").
        """

    @classmethod
    @abstractmethod
    def _get_configs(cls) -> ConfigT:
        """Return expected configuration structure.

        Returns:
            Minimum required configuration as dict or list.
        """

    def __init__(self) -> None:
        """Initialize config file, creating or updating as needed.

        Calls create_file() if file doesn't exist (which creates parent dirs and file),
        validates content, and adds missing configs if needed.
        Idempotent and preserves user customizations.

        Raises:
            ValueError: If file cannot be made correct.
        """
        path = self.get_path()
        logger.debug(
            "Initializing config file: %s at: %s",
            self.__class__.__name__,
            path,
        )
        if not path.exists():
            self.create_file()
            self.dump(self.get_configs())

        if not self.is_correct():
            logger.info("Updating config file %s at: %s", self.__class__.__name__, path)
            config = self.add_missing_configs()
            self.dump(config)

        if not self.is_correct():
            msg = f"Config file {path} is not correct."
            raise ValueError(msg)

    @classmethod
    def create_file(cls) -> None:
        """Create the config file and its parent directories."""
        path = cls.get_path()
        logger.info("Creating config file %s at: %s", cls.__name__, path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()

    @classmethod
    @cache
    def get_configs(cls) -> ConfigT:
        """Return expected configuration structure.

        Cached to avoid multiple calls to _get_configs().

        Returns:
            Minimum required configuration as dict or list.
        """
        return cls._get_configs()

    @classmethod
    @cache
    def load(cls) -> ConfigT:
        """Load and parse configuration file.

        Cached to avoid multiple reads of same file.

        Returns:
            Parsed configuration as dict or list. Format-specific implementations
            typically return empty dict/list for empty files (opt-out behavior).
        """
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
        cls.load.cache_clear()
        cls._dump(config)
        cls.load.cache_clear()

    @classmethod
    def get_priority(cls) -> float:
        """Return initialization priority (higher = first, default 0).

        Returns:
            Priority as float. Higher numbers processed first.
        """
        return 0

    @classmethod
    def get_path(cls) -> Path:
        """Return full path by combining parent path, filename, and extension.

        Returns:
            Complete path including filename and extension.
        """
        return cls.get_parent_path() / (
            cls.get_filename() + cls.get_extension_sep() + cls.get_file_extension()
        )

    @classmethod
    def get_extension_sep(cls) -> str:
        """Return extension separator character (always ".").

        Returns:
            "." (dot character).
        """
        return "."

    @classmethod
    def get_filename(cls) -> str:
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
    def add_missing_configs(cls) -> ConfigT:
        """Merge expected config into current, preserving user customizations.

        Returns:
            Merged configuration with all expected values and user additions.

        See Also:
            pyrig.src.iterate.nested_structure_is_subset: Subset validation logic
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
        """Merge dict value during config merging (modifies actual_dict in place).

        First calls setdefault to add key if missing. Then:
        - For dict values: merges expected into actual (preserves actual values,
          adds expected values)
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
        return cls.get_path().exists() and (
            cls.is_unwanted()
            or cls.is_correct_recursively(cls.get_configs(), cls.load())
        )

    @classmethod
    def is_unwanted(cls) -> bool:
        """Check if user opted out (file exists and is empty).

        Returns:
            True if file exists and is completely empty.
        """
        return (
            cls.get_path().exists() and cls.get_path().read_text(encoding="utf-8") == ""
        )

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
    def get_definition_pkg(cls) -> ModuleType:
        """Get the package where the ConfigFile subclasses are supposed to be defined.

        Default is pyrig.dev.configs.
        But can be overridden by subclasses to define their own package.

        Returns:
            Package module where the ConfigFile subclass is defined.
        """
        return configs

    @classmethod
    def get_all_subclasses(cls) -> list[type[Self]]:
        """Discover all non-abstract ConfigFile subclasses across all packages.

        Returns:
            List of ConfigFile subclass types, sorted by priority (highest first).

        See Also:
            get_priority_subclasses: Get only subclasses with priority > 0
            init_all_subclasses: Initialize all discovered subclasses
        """
        subclasses = discover_subclasses_across_dependents(
            cls,
            pyrig,
            cls.get_definition_pkg(),
            discard_parents=True,
            exclude_abstract=True,
        )
        return cls.get_subclasses_ordered_by_priority(*subclasses)

    @classmethod
    def get_subclasses_ordered_by_priority[T: type[Self]](
        cls, *subclasses: T
    ) -> list[T]:
        """Order subclasses by priority.

        Args:
            subclasses: ConfigFile subclasses to order.

        Returns:
            List of ConfigFile subclass types, sorted by priority (highest first).
        """
        return sorted(subclasses, key=lambda x: x.get_priority(), reverse=True)

    @classmethod
    def get_priority_subclasses(cls) -> list[type[Self]]:
        """Get ConfigFile subclasses with priority > 0.

        Returns:
            List of ConfigFile subclass types with priority > 0 (highest first).

        See Also:
            get_all_subclasses: Get all subclasses regardless of priority
            init_priority_subclasses: Initialize only priority subclasses
        """
        return [cf for cf in cls.get_all_subclasses() if cf.get_priority() > 0]

    @classmethod
    def init_subclasses(
        cls,
        *subclasses: type[Self],
    ) -> None:
        """Initialize specific ConfigFile subclasses with priority-based ordering.

        Groups by priority, initializes in the order given, parallel within groups.
        Order by priority is defined in get_subclasses_ordered_by_priority.

        Args:
            subclasses: ConfigFile subclasses to initialize.

        See Also:
            init_all_subclasses: Initialize all discovered subclasses
            init_priority_subclasses: Initialize only priority subclasses
        """
        # order by priority
        subclasses_by_priority: dict[float, list[type[ConfigFile[Any]]]] = defaultdict(
            list
        )
        for cf in subclasses:
            subclasses_by_priority[cf.get_priority()].append(cf)

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
                    "Initializing %d config files with priority: %s",
                    len(cf_group),
                    priority,
                )
                list(executor.map(lambda cf: cf(), cf_group))

    @classmethod
    def init_all_subclasses(cls) -> None:
        """Initialize all discovered ConfigFile subclasses in priority order.

        See Also:
            get_all_subclasses: Discovery mechanism
            init_subclasses: Initialization mechanism
            init_priority_subclasses: Initialize only priority files
        """
        logger.info("Creating all config files")
        cls.init_subclasses(*cls.get_all_subclasses())

    @classmethod
    def init_priority_subclasses(cls) -> None:
        """Initialize only ConfigFile subclasses with priority > 0.

        See Also:
            get_priority_subclasses: Discovery mechanism
            init_subclasses: Initialization mechanism
            init_all_subclasses: Initialize all files
        """
        logger.info("Creating priority config files")
        cls.init_subclasses(*cls.get_priority_subclasses())

    @classproperty
    def L(cls) -> type[Self]:  # noqa: N802, N805
        """Get the final leaf subclass (deepest in the inheritance tree).

        Returns:
            Final leaf subclass type. Can be abstract.

        See Also:
            get_all_subclasses: Get all subclasses regardless of priority
        """
        return discover_leaf_subclass_across_dependents(
            cls=cls, dep=pyrig, load_pkg_before=cls.get_definition_pkg()
        )
