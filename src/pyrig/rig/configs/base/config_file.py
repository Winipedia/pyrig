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


            def parent_path(self) -> Path:
                '''Place in project root.'''
                return Path()


            def _configs(self) -> ConfigDict:
                '''Define expected configuration.'''
                return {
                    "app": {
                        "name": "myapp",
                        "version": "1.0.0"
                    }
                }


            def priority(self) -> float:
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

import logging
from abc import abstractmethod
from collections.abc import Generator, Iterable
from functools import cache
from pathlib import Path
from types import ModuleType
from typing import Any, Self

import typer

from pyrig.core.iterate import (
    merge_nested_structures,
    nested_structure_is_subset,
)
from pyrig.rig import configs
from pyrig.rig.cli.subcommands import mkroot
from pyrig.rig.tools.pyrigger import Pyrigger
from pyrig.rig.utils.dependency_subclass import RigDependencySubclass

logger = logging.getLogger(__name__)


type ConfigDict = dict[str, Any]
type ConfigList = list[Any]
type ConfigData = ConfigDict | ConfigList


class Priority:
    """Priority levels for config file validation ordering."""

    DEFAULT = 0
    LOW = DEFAULT + 10
    MEDIUM = LOW + 10
    HIGH = MEDIUM + 10


class ConfigFile[ConfigT: ConfigData](RigDependencySubclass):
    """Abstract base class for declarative configuration file management.

    Declarative, idempotent system for managing config files. Preserves user
    customizations while ensuring required configuration is present.

    Type Parameters:
        ConfigT: The configuration type (ConfigDict or ConfigList).

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

    def __str__(self) -> str:
        """String representation showing the config file path."""
        return f"{super().__str__()} ({self.path()})"

    @abstractmethod
    def parent_path(self) -> Path:
        """Return directory containing the config file.

        Returns:
            Path to parent directory, relative to project root.
        """

    @abstractmethod
    def stem(self) -> str:
        """Return filename stem (name without extension)."""

    @abstractmethod
    def _load(self) -> ConfigT:
        """Load and parse configuration file.

        Returns:
            Parsed configuration as dict or list. Implementations should return
            empty dict/list for empty files to support opt-out behavior.
        """

    @abstractmethod
    def _dump(self, config: ConfigT) -> None:
        """Write configuration to file.

        Args:
            config: Configuration to write (dict or list).
        """

    @abstractmethod
    def extension(self) -> str:
        """Return file extension without leading dot.

        Returns:
            File extension (e.g., "toml", "yaml", "json", "py", "md").
        """

    @abstractmethod
    def _configs(self) -> ConfigT:
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
        return -subclass().priority()

    def version_control_ignored(self) -> bool:
        """Wether this config file is ignored by version control (e.g., .gitignore).

        Default implementation returns False,
        meaning the file is tracked by version control.
        Can be overridden by subclasses to indicate the file is ignored.
        """
        return False

    def validate(self) -> None:
        """Validate config file, creating or updating as needed.

        Calls create_file() if file doesn't exist (which creates parent dirs and file),
        validates content, and adds missing configs if needed.
        Idempotent and preserves user customizations.

        Raises:
            ConfigFileValidationError: If file cannot be made correct.
        """
        path = self.path()
        logger.debug("Validating %s", self)
        if not path.exists():
            self.create_file()
            self.dump(self.configs())

        if self.is_correct():
            return

        config = self.merge_configs()
        self.dump(config)

        if not self.is_correct():
            msg = f"""Failed to validate {self} after merging and dumping configs.
Please check the file for issues and fix manually if needed.
You can delete the file and use {Pyrigger.I.cmd_args(cmd=mkroot)} to recreate it."""
            raise RuntimeError(msg)

    def create_file(self) -> None:
        """Create the config file and its parent directories."""
        path = self.path()
        typer.echo(f"Creating {self}")
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
        return cls()._configs()  # noqa: SLF001

    @classmethod
    @cache
    def load(cls) -> ConfigT:
        """Load and parse configuration file.

        Cached to avoid multiple reads of same file.

        Returns:
            Parsed configuration as dict or list. Format-specific implementations
            typically return empty dict/list for empty files (opt-out behavior).
        """
        instance = cls()
        logger.debug("Loading %s", instance)
        return instance._load()

    def dump(self, config: ConfigT) -> None:
        """Write configuration to file.

        Clears the cache before writing to ensure the dump operation reads
        the current file state if it loads, and after writing to ensure subsequent loads
        reflect the latest state.

        Args:
            config: Configuration to write (dict or list).
        """
        typer.echo(f"Updating {self}")
        self.load.cache_clear()
        self._dump(config)
        self.load.cache_clear()

    def priority(self) -> float:
        """Return validation priority (higher = first, default 0)."""
        return Priority.DEFAULT

    def path(self) -> Path:
        """Return full path by combining parent path, filename, and extension."""
        return self.parent_path() / (
            self.stem() + self.extension_separator() + self.extension()
        )

    def extension_separator(self) -> str:
        """Return extension separator character (always ".")."""
        return "."

    def merge_configs(self) -> ConfigT:
        """Merge expected config into current, preserving user customizations.

        Returns:
            Merged configuration with all expected values and user additions.

        See Also:
            pyrig.src.iterate.nested_structure_is_subset: Subset validation logic
        """
        return merge_nested_structures(subset=self.configs(), superset=self.load())

    def is_correct(self) -> bool:
        """Check if config file is valid (empty or expected is subset of actual).

        Returns:
            True if valid (opted out or contains all expected configuration).

        See Also:
            is_unwanted: Check if user opted out
            is_correct_recursively: Perform subset validation
        """
        return self.path().exists() and (
            self.is_unwanted() or self.is_correct_recursively()
        )

    def is_unwanted(self) -> bool:
        """Check if user opted out (file exists and is empty).

        Returns:
            True if file exists and is completely empty.
        """
        return self.path().exists() and self.path().stat().st_size == 0

    def is_correct_recursively(
        self,
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
        return nested_structure_is_subset(self.configs(), self.load())

    @classmethod
    def validate_subclasses(
        cls,
        subclasses: Iterable[type[Self]],
    ) -> None:
        """Validate specific ConfigFile subclasses with priority-based ordering.

        Group by priority, validate in the given order, parallel within groups.

        Args:
            subclasses: ConfigFile subclasses to validate.

        See Also:
            validate_all_subclasses: validate all discovered subclasses
        """
        tuple(cf().validate() for cf in cls.subclasses_sorted(subclasses))

    @classmethod
    def validate_all_subclasses(cls) -> None:
        """Validate all discovered ConfigFile subclasses in priority order.

        Discovers all concrete subclasses across dependents, sorts by priority,
        and validates each. This is the main entry point for validating config files.
        """
        cls.validate_subclasses(cls.concrete_subclasses())

    @classmethod
    def version_control_ignored_subclasses(cls) -> Generator[type[Self], None, None]:
        """Get config file classes that are ignored by .gitignore.

        Returns:
            Generator of ConfigFile instances whose paths match .gitignore patterns.
        """
        return (
            cf for cf in cls.concrete_subclasses() if cf().version_control_ignored()
        )

    @classmethod
    def incorrect_subclasses(cls) -> Generator[type[Self], None, None]:
        """Get config file classes whose files are not correct.

        Returns:
            Generator of ConfigFile instances whose files exist but are not correct.
        """
        return (cf for cf in cls.concrete_subclasses() if not cf().is_correct())


class ListConfigFile(ConfigFile[ConfigList]):
    """Abstract base class for list-based configuration files.

    Specifies `ConfigList` as the configuration type. Subclasses inherit
    proper typing for `load()`, `dump()`, `configs()`, etc.

    Subclasses must implement:
        - `parent_path`: Directory containing the config file
        - `extension`: File extension without leading dot
        - `_configs`: Expected configuration as list
        - `_load`: Load and parse the file
        - `_dump`: Write configuration to file
    """


class DictConfigFile(ConfigFile[ConfigDict]):
    """Abstract base class for dict-based configuration files.

    Specifies ConfigDict as the configuration type. Subclasses inherit
    proper typing for load(), dump(), configs(), etc.

    Subclasses must implement:
        - `parent_path`: Directory containing the config file
        - `extension`: File extension without leading dot
        - `_configs`: Expected configuration as dict
        - `_load`: Load and parse the file
        - `_dump`: Write configuration to file
    """
