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
"""

import inspect
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import pyrig
from pyrig.dev import configs
from pyrig.src.iterate import nested_structure_is_subset
from pyrig.src.modules.package import (
    get_all_nonabst_subcls_from_mod_in_all_deps_depen_on_dep,
)
from pyrig.src.string import split_on_uppercase


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
