"""Core load, merge, validate, and dump lifecycle for configuration files."""

from abc import abstractmethod
from collections.abc import Iterable, Iterator
from functools import cache
from pathlib import Path
from types import ModuleType
from typing import Any, Self

import typer
from pyrig_runtime.core.dependencies.subclass import DependencySubclass

from pyrig.core.iterate import (
    merge_nested_structures,
    nested_structure_is_subset,
)
from pyrig.rig import configs


class ConfigFile[ConfigT: dict[str, Any] | list[Any]](DependencySubclass):
    """Abstract base class for declarative configuration file management.

    Implements an idempotent, declarative system for managing configuration
    files across a project. Subclasses declare the required structure and the
    system ensures that structure is present on disk, merging missing or
    mismatched values while preserving any extra keys the user has added.

    The type parameter `ConfigT` is the configuration data type, either
    `dict[str, Any]` or `list[Any]`.
    """

    @abstractmethod
    def _configs(self) -> ConfigT:
        """Return the minimum required configuration structure.

        Keys or items present on disk but absent from this return value are
        preserved unchanged.

        Returns:
            Required configuration as a dict or list.
        """

    @abstractmethod
    def _dump(self, configs: ConfigT) -> None:
        """Write configuration to the file on disk.

        Args:
            configs: Configuration data to write.
        """

    @abstractmethod
    def _load(self) -> ConfigT:
        """Load and parse the configuration file from disk.

        Returns:
            Parsed configuration as a dict or list.
        """

    @abstractmethod
    def extension(self) -> str:
        """Return the file extension without the leading dot.

        Returns:
            The extension string, e.g. `"toml"`, `"yaml"`, or `"py"`.
        """

    @abstractmethod
    def parent_path(self) -> Path:
        """Return the directory that will contain the config file.

        Returns:
            Path to the parent directory, typically relative to the project root.
        """

    @abstractmethod
    def stem(self) -> str:
        """Return the filename without its extension.

        Returns:
            The file stem, e.g. `"pyproject"` for `pyproject.toml`.
        """

    def __str__(self) -> str:
        """Add the file path to the string representation.

        Returns:
            The class's string representation, followed by the file path in parentheses.
        """
        return f"{super().__str__()} ({self.path()})"

    @classmethod
    def discovery_module(cls) -> ModuleType:
        """Return the `pyrig.rig.configs` package, scoping discovery to config files.

        Returns:
            The `pyrig.rig.configs` package module.
        """
        return configs

    @classmethod
    def sort_key(cls) -> float:
        """Return a sort key that places higher-priority subclasses first.

        Returns:
            Negative of the subclass priority value, so ascending sort
            orders higher-priority subclasses first.
        """
        return -cls().priority()

    @classmethod
    @cache
    def configs(cls) -> ConfigT:
        """Return the required configuration structure.

        The result is cached per class and reused on every subsequent access.

        Returns:
            Minimum required configuration as a dict or list.
        """
        return cls()._configs()  # noqa: SLF001

    @classmethod
    @cache
    def load(cls) -> ConfigT:
        """Load and return the current file contents.

        The result is cached per class and reused on every subsequent access,
        until `dump()` clears the cache.

        Returns:
            Parsed configuration as a dict or list.
        """
        instance = cls()
        return instance._load()

    @classmethod
    def version_control_ignored_subclasses(cls) -> Iterator[type[Self]]:
        """Yield config file classes whose files are excluded from version control.

        Yields:
            `ConfigFile` subclasses for which `version_control_ignored()`
            returns `True`.
        """
        return (
            cf for cf in cls.concrete_subclasses() if cf().version_control_ignored()
        )

    @classmethod
    def validate_concrete_subclasses(cls) -> tuple[type[Self], ...]:
        """Discover and validate every concrete `ConfigFile` subclass.

        Returns:
            Tuple of subclasses that were created or updated.
            Empty if all were already correct.
        """
        return cls.validate_subclasses(cls.concrete_subclasses())

    @classmethod
    def validate_subclasses(
        cls,
        subclasses: Iterable[type[Self]],
    ) -> tuple[type[Self], ...]:
        """Validate a specific collection of `ConfigFile` subclasses.

        Sorts the given subclasses by priority (higher priority first) and
        validates each one in order.

        Args:
            subclasses: `ConfigFile` subclasses to validate.

        Returns:
            Tuple of subclasses that were created or updated.
            Empty if all were already correct.
        """
        return tuple(
            cf for cf in cls.sort_subclasses(subclasses) if not cf().validate()
        )

    def validate(self) -> bool:
        """Validate the config file, creating or updating it as needed.

        Creates the file if it is missing, or merges in any required values
        it is missing, leaving an already-correct file untouched. Idempotent
        and safe to call repeatedly.

        Returns:
            `True` if the file was already correct and required no changes;
            `False` if it was created or updated.

        Raises:
            RuntimeError: If the file is still not correct after merging in
                the required configuration, typically indicating a manual
                conflict in the file.
        """
        path = self.path()
        if not path.exists():
            self.create_file()
            self.dump(self.configs())
            return False

        if self.is_correct():
            return True

        config = self.merge_configs()
        self.dump(config)

        if not self.is_correct():
            msg = f"""failed to validate {self}"""
            raise RuntimeError(msg)
        return False

    def create_file(self) -> None:
        """Create the config file and any missing parent directories.

        Touches the file, creating it empty, after ensuring the full parent
        directory tree exists. Echoes the created file path to stdout.
        """
        path = self.path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
        typer.echo(f"Created {self}")

    def path(self) -> Path:
        """Return the full path to the config file."""
        return self.parent_path() / self.filename()

    def filename(self) -> str:
        """Return the filename of the config file, including extension.

        Returns:
            The config file's filename, e.g. `"config.toml"`.
        """
        return f"{self.stem()}{self.extension_separator()}{self.extension()}"

    def extension_separator(self) -> str:
        """Return the character separating the stem from the extension, `"."`."""
        return "."

    def dump(self, configs: ConfigT) -> None:
        """Write configuration to disk and keep the load cache consistent.

        Clears the `load()` cache afterward, so the new content is read on
        subsequent `load()` calls instead of the stale cached value.
        Echoes the updated file path to stdout.

        Args:
            configs: Configuration data to write.
        """
        self._dump(configs)
        self.load.cache_clear()
        typer.echo(f"Updated {self}")

    def is_correct(self) -> bool:
        """Return whether the config file passes validation.

        A file is considered correct if it contains at least all the keys and
        values declared in `configs()` (additional keys are allowed).

        Returns:
            `True` if all required configuration is present in the file.
        """
        return self.is_correct_recursively()

    def is_correct_recursively(self) -> bool:
        """Return whether `configs()` is recursively contained within `load()`.

        Nested dicts and lists are compared level by level rather than for
        exact equality, so extra keys or items anywhere in `load()` do not
        cause a mismatch.

        Returns:
            `True` if every key and value required by `configs()` is present
            in `load()`.
        """
        return nested_structure_is_subset(self.configs(), self.load())

    def merge_configs(self) -> ConfigT:
        """Merge the required configuration into the current file contents.

        Fills in every key or list item that is present in `configs()` but
        missing from, or different in, `load()`. Keys present only in the
        loaded file are left untouched, preserving user customizations.

        Returns:
            Updated configuration containing both required and existing values.
        """
        return merge_nested_structures(subset=self.configs(), superset=self.load())

    def priority(self) -> float:
        """Return the validation priority for this config file.

        Higher values cause the file to be validated earlier relative to others.
        Defaults to `Priority.DEFAULT`. Override in subclasses that must be
        validated before others.

        Returns:
            Validation priority as a float.
        """
        return Priority.DEFAULT

    def version_control_ignored(self) -> bool:
        """Return whether this config file is excluded from version control.

        Defaults to `False` (tracked by version control). Override in
        subclasses whose file is git-ignored.

        Returns:
            `True` if the file is git-ignored; `False` otherwise.
        """
        return False


class ListConfigFile(ConfigFile[list[str]]):
    """Abstract base for config files whose content is a list.

    Binds the `ConfigT` type parameter to `list[str]`, so subclasses work
    with a concretely typed list instead of the generic base type.
    """


class DictConfigFile(ConfigFile[dict[str, Any]]):
    """Abstract base for config files whose content is a dict.

    Binds the `ConfigT` type parameter to `dict[str, Any]`, so subclasses
    work with a concretely typed dict instead of the generic base type.
    """


class Priority:
    """Helpers for controlling config file validation order.

    A config file's `priority()` is a float; higher values are validated
    earlier. `DEFAULT` is the baseline used by most files. Rather than
    hard-coding absolute values, use `increase()` / `decrease()` to
    position a config file one `STEP` before or after another file's priority.

    Attributes:
        STEP: Spacing between adjacent priority levels.
        DEFAULT: Baseline priority used by most config files.
    """

    STEP = 10
    DEFAULT = 0

    @classmethod
    def decrease(cls, priority: float) -> float:
        """Return a priority one `STEP` lower, so it is validated later.

        Args:
            priority: The base priority to lower.

        Returns:
            `priority` decreased by one `STEP`.
        """
        return priority - cls.STEP

    @classmethod
    def increase(cls, priority: float) -> float:
        """Return a priority one `STEP` higher, so it is validated earlier.

        Args:
            priority: The base priority to raise.

        Returns:
            `priority` increased by one `STEP`.
        """
        return priority + cls.STEP
