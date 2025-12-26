"""Abstract base class for declarative configuration file management.

This module provides the ConfigFile abstract base class, which is the foundation
of pyrig's configuration system. ConfigFile enables declarative, automated
management of project configuration files through:

Core Capabilities:
    - **Automatic Discovery**: Finds all ConfigFile subclasses across packages
    - **Subset Validation**: User configs can extend but not contradict base
    - **Intelligent Merging**: Adds missing values without removing existing ones
    - **Priority-Based Init**: Control initialization order for dependencies
    - **Parallel Execution**: Same-priority files initialized concurrently
    - **Opt-Out Support**: Empty files signal user doesn't want that config
    - **Idempotent Operations**: Safe to run multiple times

The ConfigFile System:
    ConfigFile is the heart of pyrig's project automation. When you run
    `pyrig mkroot` or call `ConfigFile.init_all_subclasses()`, the system:

    1. Discovers all non-abstract ConfigFile subclasses across all packages
       that depend on pyrig (using `get_all_subclasses()`)
    2. Groups subclasses by priority (via `get_priority()`)
    3. Initializes each priority group in descending order (highest first)
    4. Within each group, initializes files in parallel via ThreadPoolExecutor
    5. Each ConfigFile initialization:
       - Creates parent directories if needed
       - Creates file with default content if missing
       - Validates existing content via subset checking
       - Adds missing configuration values
       - Raises ValueError if file cannot be made correct

Subclass Requirements:
    All ConfigFile subclasses must implement these abstract methods:

    - `get_parent_path()`: Return Path to directory containing the file
    - `get_file_extension()`: Return file extension without leading dot
    - `get_configs()`: Return expected configuration structure (dict or list)
    - `load()`: Load and parse the file, returning dict or list
    - `dump(config)`: Write configuration to the file

    Optionally override:

    - `get_priority()`: Return float priority (default 0, higher = first)
    - `get_filename()`: Return filename without extension (auto-derived from class name)

Filename Derivation:
    By default, filenames are automatically derived from the class name:
    - Abstract parent class names are removed as suffixes
    - Remaining name is converted to snake_case
    - Example: `PyprojectConfigFile` -> `pyproject`
    - Example: `PreCommitConfigFile` -> `pre_commit`

Subset Validation:
    The system uses `nested_structure_is_subset()` to validate configurations.
    A file is "correct" if:
    - It's empty (user opted out), OR
    - Expected config is a subset of actual config

    This allows users to:
    - Add extra configuration keys
    - Extend lists with additional items
    - Override values (as long as required structure exists)

Priority System:
    ConfigFiles can specify initialization priority via `get_priority()`:
    - Higher numbers are initialized first
    - Default priority is 0
    - Use priorities when one config depends on another
    - Example: pyproject.toml has priority 100 (initialized first)
    - Files with same priority are initialized in parallel

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
            def get_configs(cls) -> dict[str, Any]:
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
    pyrig.src.modules.package.get_all_nonabst_subcls_from_mod_in_all_deps_depen_on_dep:
        Subclass discovery mechanism
"""

import inspect
import logging
from abc import ABC, abstractmethod
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import pyrig
from pyrig.dev import configs
from pyrig.src.iterate import nested_structure_is_subset
from pyrig.src.modules.package import (
    get_all_nonabst_subcls_from_mod_in_all_deps_depen_on_dep,
)
from pyrig.src.string import split_on_uppercase

logger = logging.getLogger(__name__)


class ConfigFile(ABC):
    """Abstract base class for declarative configuration file management.

    ConfigFile provides a declarative system for managing project configuration
    files. Subclasses declare what a config file should contain, and the system
    ensures the file matches that specification while preserving user customizations.

    The system is designed around these principles:
    - **Declarative**: Define what should exist, not how to create it
    - **Idempotent**: Safe to run multiple times, no duplicate additions
    - **User-Friendly**: Preserves customizations, only adds missing values
    - **Fail-Safe**: Validates final state, raises if cannot be made correct

    Initialization Process:
        When a ConfigFile is instantiated (via `__init__()`), it:

        1. Creates parent directories if they don't exist
        2. Creates the file if it doesn't exist, with default content
        3. Checks if file is correct via `is_correct()`
        4. If not correct, adds missing values via `add_missing_configs()`
        5. Validates again - raises ValueError if still not correct

    Subclass Requirements:
        All subclasses must implement these abstract methods:

        - `get_parent_path()`: Return Path to directory containing the file
        - `get_file_extension()`: Return file extension (e.g., "toml", "yaml")
        - `get_configs()`: Return expected configuration (dict or list)
        - `load()`: Load and parse the file, returning dict or list
        - `dump(config)`: Write configuration to the file

    Optional Overrides:
        Subclasses can optionally override:

        - `get_priority()`: Return initialization priority (default 0)
        - `get_filename()`: Return filename without extension (auto-derived)

    Filename Derivation:
        By default, `get_filename()` derives the filename from the class name:
        - Removes abstract parent class names as suffixes
        - Converts remaining name to snake_case
        - Example: `PyprojectConfigFile` -> `pyproject`
        - Example: `GitIgnoreConfigFile` -> `git_ignore`

    Subset Validation:
        A file is considered "correct" if:
        - It's empty (user opted out), OR
        - Expected config is a subset of actual config

        This allows users to add extra keys, extend lists, and customize values
        while ensuring required configuration is present.

    Class Methods:
        Discovery and Initialization:
        - `get_all_subclasses()`: Find all ConfigFile subclasses across packages
        - `get_priority_subclasses()`: Get subclasses with priority > 0
        - `init_subclasses(*subclasses)`: Initialize specific subclasses
        - `init_all_subclasses()`: Initialize all discovered subclasses
        - `init_priority_subclasses()`: Initialize only priority subclasses

        File Operations:
        - `get_path()`: Get full path to the config file
        - `get_filename()`: Get filename without extension
        - `is_correct()`: Check if file matches expected configuration
        - `is_unwanted()`: Check if user opted out (empty file)
        - `add_missing_configs()`: Merge expected config into actual

    Example:
        Create a custom config file::

            from pathlib import Path
            from typing import Any
            from pyrig.dev.configs.base.yaml import YamlConfigFile

            class MyConfigFile(YamlConfigFile):
                '''Manages myconfig.yaml.'''

                @classmethod
                def get_parent_path(cls) -> Path:
                    return Path()

                @classmethod
                def get_configs(cls) -> dict[str, Any]:
                    return {
                        "setting": "value",
                        "enabled": True
                    }

        Then initialize::

            MyConfigFile()  # Creates/updates myconfig.yaml

    See Also:
        pyrig.dev.configs: Package-level documentation
        pyrig.dev.configs.base.toml.TomlConfigFile: TOML file base class
        pyrig.dev.configs.base.yaml.YamlConfigFile: YAML file base class
        pyrig.src.iterate.nested_structure_is_subset: Subset validation
    """

    @classmethod
    @abstractmethod
    def get_parent_path(cls) -> Path:
        """Get the directory containing the config file.

        Subclasses must implement this to specify where the config file should
        be located. Common patterns:
        - `Path()` for project root
        - `Path(".github")` for GitHub-specific files
        - `Path("docs")` for documentation files

        Returns:
            Path to the parent directory, relative to project root.

        Example:
            Place file in project root::

                @classmethod
                def get_parent_path(cls) -> Path:
                    return Path()

            Place file in .github directory::

                @classmethod
                def get_parent_path(cls) -> Path:
                    return Path(".github")
        """

    @classmethod
    @abstractmethod
    def load(cls) -> dict[str, Any] | list[Any]:
        """Load and parse the configuration file from disk.

        Subclasses must implement this to read and parse the file in the
        appropriate format (YAML, TOML, JSON, etc.). The implementation should:
        - Read the file from `cls.get_path()`
        - Parse the content into a dict or list
        - Return empty dict/list if file is empty (opt-out case)

        Returns:
            The parsed configuration as a dict or list. Returns empty dict/list
            if the file is empty (indicating user opted out).

        Example:
            For TOML files::

                @classmethod
                def load(cls) -> dict[str, Any]:
                    import tomllib
                    path = cls.get_path()
                    if path.read_text() == "":
                        return {}
                    with path.open("rb") as f:
                        return tomllib.load(f)
        """

    @classmethod
    @abstractmethod
    def dump(cls, config: dict[str, Any] | list[Any]) -> None:
        """Write configuration to the file.

        Subclasses must implement this to serialize and write the configuration
        in the appropriate format. The implementation should:
        - Serialize the config to the appropriate format
        - Write to `cls.get_path()`
        - Handle formatting/indentation appropriately

        Args:
            config: The configuration to write. Can be a dict or list depending
                on the file format.

        Example:
            For TOML files::

                @classmethod
                def dump(cls, config: dict[str, Any]) -> None:
                    import tomli_w
                    path = cls.get_path()
                    with path.open("wb") as f:
                        tomli_w.dump(config, f)
        """

    @classmethod
    @abstractmethod
    def get_file_extension(cls) -> str:
        """Get the file extension for this config file.

        Subclasses must implement this to specify the file extension. The
        extension should NOT include the leading dot.

        Returns:
            The file extension without the leading dot (e.g., "toml", "yaml",
            "json", "py", "md").

        Example:
            For TOML files::

                @classmethod
                def get_file_extension(cls) -> str:
                    return "toml"

            For YAML files::

                @classmethod
                def get_file_extension(cls) -> str:
                    return "yaml"
        """

    @classmethod
    @abstractmethod
    def get_configs(cls) -> dict[str, Any] | list[Any]:
        """Get the expected configuration structure.

        Subclasses must implement this to define what configuration should be
        present in the file. The returned structure is used for:
        - Creating new files with default content
        - Validating existing files via subset checking
        - Adding missing values to incomplete files

        The structure should represent the minimum required configuration. Users
        can add extra keys/values, but these will be preserved.

        Returns:
            The expected configuration as a dict or list. This is the minimum
            configuration that must be present in the file.

        Example:
            For a simple config file::

                @classmethod
                def get_configs(cls) -> dict[str, Any]:
                    return {
                        "version": "1.0",
                        "settings": {
                            "enabled": True
                        }
                    }

            For a list-based config::

                @classmethod
                def get_configs(cls) -> list[Any]:
                    return [
                        {"name": "item1", "value": 1},
                        {"name": "item2", "value": 2}
                    ]
        """

    def __init__(self) -> None:
        """Initialize the config file, creating or updating as needed.

        This is the main entry point for ConfigFile initialization. It performs
        the complete lifecycle of ensuring a config file is correct:

        1. Creates parent directories if they don't exist
        2. Creates the file if it doesn't exist, with default content from
           `get_configs()`
        3. Checks if the file is correct via `is_correct()`
        4. If not correct, adds missing values via `add_missing_configs()`
        5. Validates again - raises ValueError if still not correct

        The process is idempotent: running it multiple times has the same effect
        as running it once. User customizations are preserved - only missing
        values are added.

        Raises:
            ValueError: If the config file cannot be made correct after attempting
                to add missing configurations. This indicates either:
                - The file format is invalid and cannot be parsed
                - The load/dump implementation has a bug
                - The file is locked or has permission issues

        Example:
            Initialize a single config file::

                from pyrig.dev.configs.pyproject import PyprojectConfigFile
                PyprojectConfigFile()  # Creates/updates pyproject.toml

            Initialize all config files::

                from pyrig.dev.configs.base.base import ConfigFile
                ConfigFile.init_all_subclasses()  # Creates/updates all configs
        """
        path = self.get_path()
        logger.debug(
            "Initializing config file: %s at: %s",
            self.__class__.__name__,
            path,
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            logger.info("Creating config file %s at: %s", self.__class__.__name__, path)
            path.touch()
            self.dump(self.get_configs())

        if not self.is_correct():
            logger.info("Updating config file %s at: %s", self.__class__.__name__, path)
            config = self.add_missing_configs()
            self.dump(config)

        if not self.is_correct():
            msg = f"Config file {path} is not correct."
            raise ValueError(msg)

    @classmethod
    def get_priority(cls) -> float:
        """Get the initialization priority for this config file.

        Priority controls the order in which ConfigFiles are initialized. Higher
        priority files are initialized first. Files with the same priority are
        initialized in parallel.

        Use priorities when one config file depends on another. For example,
        pyproject.toml has priority 100 because other configs may read from it.

        Returns:
            The priority as a float. Higher numbers are processed first.
            Default is 0 (no specific priority).

        Example:
            High priority (initialized first)::

                @classmethod
                def get_priority(cls) -> float:
                    return 100  # Initialize before most other files

            Normal priority (initialized with other normal files)::

                @classmethod
                def get_priority(cls) -> float:
                    return 0  # Default, no specific order needed

            Low priority (initialized last)::

                @classmethod
                def get_priority(cls) -> float:
                    return -10  # Initialize after other files
        """
        return 0

    @classmethod
    def get_path(cls) -> Path:
        """Get the full path to the config file.

        Combines the parent path, filename, and extension to create the complete
        path. The path is constructed as:
        `get_parent_path() / (get_filename() + "." + get_file_extension())`

        Returns:
            Complete path including filename and extension.

        Example:
            For PyprojectConfigFile::

                get_parent_path() -> Path()
                get_filename() -> "pyproject"
                get_file_extension() -> "toml"
                get_path() -> Path("pyproject.toml")

            For GitIgnoreConfigFile::

                get_parent_path() -> Path()
                get_filename() -> "git_ignore"
                get_file_extension() -> ""
                get_path() -> Path(".gitignore")
        """
        return cls.get_parent_path() / (
            cls.get_filename() + cls.get_extension_sep() + cls.get_file_extension()
        )

    @classmethod
    def get_extension_sep(cls) -> str:
        """Get the extension separator character.

        Returns the character used to separate the filename from the extension.
        This is always "." for standard files.

        Returns:
            The string "." (dot character).

        Note:
            This method exists to allow subclasses to override it for special
            cases (e.g., dotfiles like .gitignore where the "extension" is empty).
        """
        return "."

    @classmethod
    def get_filename(cls) -> str:
        """Derive the filename from the class name.

        Automatically generates the filename by:
        1. Taking the class name (e.g., "PyprojectConfigFile")
        2. Removing abstract parent class names as suffixes
           (e.g., removes "ConfigFile")
        3. Converting the remaining name to snake_case
           (e.g., "Pyproject" -> "pyproject")

        This allows you to name your class descriptively without manually
        specifying the filename.

        Returns:
            The filename without extension.

        Example:
            Class name to filename mapping::

                PyprojectConfigFile -> "pyproject"
                GitIgnoreConfigFile -> "git_ignore"
                PreCommitConfigFile -> "pre_commit"
                MkDocsConfigFile -> "mk_docs"

        Note:
            Subclasses can override this method to specify a custom filename
            that doesn't follow the automatic derivation.
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

        Intelligently adds missing keys and values from the expected configuration
        to the current configuration. This method:

        1. Loads the current configuration from disk
        2. Gets the expected configuration from `get_configs()`
        3. Uses `nested_structure_is_subset()` to find missing values
        4. Adds missing values via callbacks (`add_missing_dict_val`,
           `insert_missing_list_val`)
        5. Returns the merged configuration

        The merging process preserves user customizations:
        - Existing keys are NOT removed
        - Existing values are NOT overwritten (unless they're nested dicts)
        - Only missing keys/values are added

        Returns:
            The merged configuration with all expected values present and all
            user customizations preserved.

        Example:
            Expected config::

                {"a": 1, "b": {"c": 2}}

            Current config::

                {"b": {"c": 2, "d": 3}, "e": 4}

            Merged result::

                {"a": 1, "b": {"c": 2, "d": 3}, "e": 4}
                # Added "a": 1
                # Preserved "d": 3 and "e": 4

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
        """Add a missing dictionary value during config merging.

        This callback is invoked by `nested_structure_is_subset()` when a key
        from the expected configuration is missing or incorrect in the actual
        configuration.

        The behavior depends on the value types:
        - If key is missing: Add it with the expected value
        - If both values are dicts: Recursively merge them
        - Otherwise: Replace with expected value

        Args:
            expected_dict: The expected configuration dictionary containing the
                key that should be present.
            actual_dict: The actual configuration dictionary to update. This is
                modified in place.
            key: The key to add or update in actual_dict.

        Example:
            Missing key::

                expected_dict = {"a": 1}
                actual_dict = {}
                add_missing_dict_val(expected_dict, actual_dict, "a")
                # actual_dict is now {"a": 1}

            Nested dict merge::

                expected_dict = {"a": {"b": 1}}
                actual_dict = {"a": {"c": 2}}
                add_missing_dict_val(expected_dict, actual_dict, "a")
                # actual_dict is now {"a": {"b": 1, "c": 2}}
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

        This callback is invoked by `nested_structure_is_subset()` when a value
        from the expected list is missing in the actual list at the given index.

        The value is inserted at the specified index, shifting existing values
        to the right.

        Args:
            expected_list: The expected list containing the value that should
                be present.
            actual_list: The actual list to update. This is modified in place.
            index: The index at which to insert the missing value.

        Example:
            Insert missing value::

                expected_list = [1, 2, 3]
                actual_list = [1, 3]
                insert_missing_list_val(expected_list, actual_list, 1)
                # actual_list is now [1, 2, 3]
        """
        actual_list.insert(index, expected_list[index])

    @classmethod
    def is_correct(cls) -> bool:
        """Check if the configuration file is valid.

        A file is considered "correct" if it meets one of these conditions:
        1. The file is empty (user opted out via `is_unwanted()`)
        2. The expected config is a subset of the actual config

        The subset check ensures that all required configuration is present
        while allowing users to add extra keys, extend lists, and customize
        values.

        Returns:
            True if the configuration is valid (either opted out or contains
            all expected configuration).

        Example:
            Expected config::

                {"a": 1, "b": {"c": 2}}

            Valid actual configs::

                ""  # Empty file (opted out)
                {"a": 1, "b": {"c": 2}}  # Exact match
                {"a": 1, "b": {"c": 2, "d": 3}}  # Extra key "d"
                {"a": 1, "b": {"c": 2}, "e": 4}  # Extra key "e"

            Invalid actual configs::

                {"a": 1}  # Missing "b"
                {"a": 1, "b": {}}  # Missing "c"
                {"a": 2, "b": {"c": 2}}  # Wrong value for "a"

        See Also:
            is_unwanted: Check if user opted out
            is_correct_recursively: Perform subset validation
        """
        return cls.is_unwanted() or cls.is_correct_recursively(
            cls.get_configs(), cls.load()
        )

    @classmethod
    def is_unwanted(cls) -> bool:
        """Check if the user has opted out of this config file.

        An empty file is interpreted as the user explicitly opting out of this
        configuration. This allows users to disable specific config files by
        creating an empty file at the expected path.

        Returns:
            True if the file exists and is completely empty (zero bytes).

        Example:
            Opt out of a config file::

                # Create empty file to opt out
                touch pyproject.toml

                # is_unwanted() returns True
                # is_correct() returns True (opted out is valid)
                # File will not be modified

        Note:
            This is different from a file that doesn't exist. A non-existent
            file will be created with default content. An empty file will be
            left empty.
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

        Performs deep subset validation by recursively comparing nested
        dictionaries and lists. This is a thin wrapper around
        `nested_structure_is_subset()` for clarity.

        Args:
            expected_config: The expected configuration structure. This is what
                must be present in the actual config.
            actual_config: The actual configuration to validate. This can contain
                extra keys/values beyond what's expected.

        Returns:
            True if expected is a subset of actual (all expected keys/values are
            present in actual, possibly with additional keys/values).

        Example:
            Dict subset::

                expected = {"a": 1, "b": {"c": 2}}
                actual = {"a": 1, "b": {"c": 2, "d": 3}, "e": 4}
                is_correct_recursively(expected, actual)  # True

            List subset::

                expected = [1, 2]
                actual = [1, 2, 3]
                is_correct_recursively(expected, actual)  # True

        See Also:
            pyrig.src.iterate.nested_structure_is_subset: Core subset logic
        """
        return nested_structure_is_subset(expected_config, actual_config)

    @classmethod
    def get_all_subclasses(cls) -> list[type["ConfigFile"]]:
        """Discover all non-abstract ConfigFile subclasses across all packages.

        Searches all packages that depend on pyrig for ConfigFile subclasses.
        This enables automatic discovery of config files defined in:
        - pyrig itself
        - Projects using pyrig
        - Libraries that extend pyrig

        The discovery process:
        1. Finds all packages that depend on pyrig
        2. Searches each package's `configs` module for ConfigFile subclasses
        3. Filters out abstract classes (those with unimplemented abstract methods)
        4. Discards parent classes when child classes are present
        5. Sorts by priority (highest first)

        Returns:
            List of ConfigFile subclass types, sorted by priority in descending
            order (highest priority first).

        Example:
            Discover all config files::

                from pyrig.dev.configs.base.base import ConfigFile
                all_configs = ConfigFile.get_all_subclasses()
                for config_cls in all_configs:
                    priority = config_cls.get_priority()
                    print(f"{config_cls.__name__}: priority {priority}")

        See Also:
            get_priority_subclasses: Get only subclasses with priority > 0
            init_all_subclasses: Initialize all discovered subclasses
        """
        subclasses = get_all_nonabst_subcls_from_mod_in_all_deps_depen_on_dep(
            cls,
            pyrig,
            configs,
            discard_parents=True,
        )
        return sorted(subclasses, key=lambda x: x.get_priority(), reverse=True)

    @classmethod
    def get_priority_subclasses(cls) -> list[type["ConfigFile"]]:
        """Get all ConfigFile subclasses with explicit priority (> 0).

        Returns only subclasses that have a priority greater than 0. This is
        useful for initializing only the most critical config files (like
        pyproject.toml) without initializing all config files.

        Returns:
            List of ConfigFile subclass types with priority > 0, sorted by
            priority in descending order (highest priority first).

        Example:
            Initialize only priority config files::

                from pyrig.dev.configs.base.base import ConfigFile
                priority_configs = ConfigFile.get_priority_subclasses()
                # Might return: [PyprojectConfigFile, GitIgnoreConfigFile]
                # Won't return: [MkDocsConfigFile, ReadmeConfigFile]

        See Also:
            get_all_subclasses: Get all subclasses regardless of priority
            init_priority_subclasses: Initialize only priority subclasses
        """
        return [cf for cf in cls.get_all_subclasses() if cf.get_priority() > 0]

    @classmethod
    def init_subclasses(
        cls,
        *subclasses: type["ConfigFile"],
    ) -> None:
        """Initialize specific ConfigFile subclasses with priority-based ordering.

        Groups the provided subclasses by priority and initializes them in
        descending priority order (highest first). Within each priority group,
        subclasses are initialized in parallel using a ThreadPoolExecutor.

        This enables:
        - Dependency management (high-priority files initialized first)
        - Performance optimization (parallel initialization within priority groups)
        - Controlled initialization order

        Args:
            subclasses: The ConfigFile subclasses to initialize. Can be any
                number of ConfigFile subclass types.

        Example:
            Initialize specific config files::

                from pyrig.dev.configs.pyproject import PyprojectConfigFile
                from pyrig.dev.configs.git.gitignore import GitIgnoreConfigFile

                ConfigFile.init_subclasses(
                    PyprojectConfigFile,
                    GitIgnoreConfigFile
                )

            Priority-based initialization::

                # Given:
                # PyprojectConfigFile.get_priority() -> 100
                # GitIgnoreConfigFile.get_priority() -> 50
                # MkDocsConfigFile.get_priority() -> 50

                ConfigFile.init_subclasses(
                    PyprojectConfigFile,
                    GitIgnoreConfigFile,
                    MkDocsConfigFile
                )

                # Execution order:
                # 1. PyprojectConfigFile (priority 100)
                # 2. GitIgnoreConfigFile and MkDocsConfigFile in parallel (priority 50)

        See Also:
            init_all_subclasses: Initialize all discovered subclasses
            init_priority_subclasses: Initialize only priority subclasses
        """
        subclasses_by_priority: dict[float, list[type[ConfigFile]]] = defaultdict(list)
        for cf in subclasses:
            subclasses_by_priority[cf.get_priority()].append(cf)

        biggest_group = max(subclasses_by_priority.values(), key=len)
        with ThreadPoolExecutor(max_workers=len(biggest_group)) as executor:
            for priority, cf_group in subclasses_by_priority.items():
                logger.debug("Initializing config files with priority: %s", priority)
                list(executor.map(lambda cf: cf(), cf_group))

    @classmethod
    def init_all_subclasses(cls) -> None:
        """Initialize all discovered ConfigFile subclasses.

        Discovers all ConfigFile subclasses across all packages and initializes
        them in priority order. This is the main entry point for creating a
        complete project configuration.

        This method:
        1. Calls `get_all_subclasses()` to discover all ConfigFile subclasses
        2. Calls `init_subclasses()` to initialize them in priority order
        3. Logs the initialization process

        Example:
            Create all config files::

                from pyrig.dev.configs.base.base import ConfigFile
                ConfigFile.init_all_subclasses()

                # Creates/updates:
                # - pyproject.toml
                # - .gitignore
                # - .pre-commit-config.yaml
                # - mkdocs.yml
                # - README.md
                # - And all other discovered ConfigFile subclasses

        See Also:
            get_all_subclasses: Discovery mechanism
            init_subclasses: Initialization mechanism
            init_priority_subclasses: Initialize only priority files
        """
        logger.info("Creating all config files")
        cls.init_subclasses(*cls.get_all_subclasses())

    @classmethod
    def init_priority_subclasses(cls) -> None:
        """Initialize only ConfigFile subclasses with explicit priority (> 0).

        Discovers and initializes only the ConfigFile subclasses that have a
        priority greater than 0. This is useful for quick initialization of
        critical config files without creating all config files.

        This method:
        1. Calls `get_priority_subclasses()` to get priority subclasses
        2. Calls `init_subclasses()` to initialize them in priority order
        3. Logs the initialization process

        Example:
            Create only priority config files::

                from pyrig.dev.configs.base.base import ConfigFile
                ConfigFile.init_priority_subclasses()

                # Might create/update:
                # - pyproject.toml (priority 100)
                # - .gitignore (priority 50)
                # But NOT:
                # - mkdocs.yml (priority 0)
                # - README.md (priority 0)

        See Also:
            get_priority_subclasses: Discovery mechanism
            init_subclasses: Initialization mechanism
            init_all_subclasses: Initialize all files
        """
        logger.info("Creating priority config files")
        cls.init_subclasses(*cls.get_priority_subclasses())
