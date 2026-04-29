"""Abstract base class for declarative configuration file management."""

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
    """Numeric constants for controlling config file validation order.

    Higher values cause a config file to be validated earlier.
    Use these constants instead of raw integers for clarity.
    """

    DEFAULT = 0
    LOW = DEFAULT + 10
    MEDIUM = LOW + 10
    HIGH = MEDIUM + 10


class ConfigFile[ConfigT: ConfigData](RigDependencySubclass):
    """Abstract base class for declarative configuration file management.

    Implements an idempotent, declarative system for managing configuration
    files across a project. Subclasses declare the required structure via
    ``_configs()`` and the system ensures that structure is present on disk,
    merging missing values while preserving any extra keys the user has added.

    Type Parameters:
        ConfigT: The configuration data type, either ``ConfigDict`` or
            ``ConfigList``.

    Subclass Requirements:
        Concrete subclasses must implement the following abstract methods:

        - ``parent_path()``: Directory where the file lives.
        - ``stem()``: Filename without the extension.
        - ``extension()``: File extension without the leading dot.
        - ``_configs()``: Minimum required configuration structure.
        - ``_load()``: Parse the file from disk.
        - ``_dump(configs)``: Write configuration to disk.

        The following methods may optionally be overridden:

        - ``priority()``: Validation order (default 0, higher = earlier).
        - ``version_control_ignored()``: Whether the file is git-ignored
          (default ``False``).

    Public API:
        The following methods are already implemented with caching.
        Do not override them:

        - ``configs()``: Cached result of ``_configs()``.
        - ``load()``: Cached result of ``_load()``.
        - ``dump(configs)``: Cache-invalidating wrapper around ``_dump(configs)``.
    """

    def __str__(self) -> str:
        """Return a string representation including the config file path.

        Returns:
            The inherited class name appended with the file path, e.g.
            ``mypackage.rig.configs.MyConfigFile (some/path/file.toml)``.
        """
        return f"{super().__str__()} ({self.path()})"

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
            The file stem, e.g. ``"pyproject"`` for ``pyproject.toml``.
        """

    @abstractmethod
    def extension(self) -> str:
        """Return the file extension without the leading dot.

        Returns:
            The extension string, e.g. ``"toml"``, ``"yaml"``, or ``"py"``.
        """

    @abstractmethod
    def _configs(self) -> ConfigT:
        """Return the minimum required configuration structure.

        Internal implementation called by the public ``configs()`` cached wrapper.
        Define all required keys and values here; keys present on disk but
        absent from this return value are preserved unchanged.

        Returns:
            Required configuration as a dict or list.
        """

    @abstractmethod
    def _load(self) -> ConfigT:
        """Load and parse the configuration file from disk.

        Internal implementation called by the public ``load()`` cached wrapper.

        Returns:
            Parsed configuration as a dict or list.
        """

    @abstractmethod
    def _dump(self, configs: ConfigT) -> None:
        """Write configuration to the file on disk.

        Internal implementation called by the public ``dump()``
        cache-invalidating wrapper.

        Args:
            configs: Configuration data to write.
        """

    @classmethod
    def definition_package(cls) -> ModuleType:
        """Return the package that scopes subclass discovery for config files.

        Overrides ``RigDependencySubclass.definition_package()`` to narrow
        the discovery namespace from ``pyrig.rig`` to ``pyrig.rig.configs``,
        ensuring only config file implementations are found.

        Returns:
            The ``pyrig.rig.configs`` package module.
        """
        return configs

    @classmethod
    def validate_all_subclasses(cls) -> None:
        """Discover and validate every concrete ``ConfigFile`` subclass.

        Discovers all concrete subclasses across all installed dependents
        and delegates to ``validate_subclasses()`` to validate them in
        priority order. This is the main entry point called by the
        ``mkroot`` CLI command.
        """
        cls.validate_subclasses(cls.concrete_subclasses())

    @classmethod
    def validate_subclasses(cls, subclasses: Iterable[type[Self]]) -> None:
        """Validate a specific collection of ``ConfigFile`` subclasses.

        Sorts the given subclasses by priority (higher priority first) and
        calls ``validate()`` on each one in order.

        Args:
            subclasses: ``ConfigFile`` subclasses to validate.
        """
        for cf in cls.subclasses_sorted(subclasses):
            cf().validate()

    @classmethod
    def version_control_ignored_subclasses(cls) -> Generator[type[Self], None, None]:
        """Yield config file classes whose files are excluded from version control.

        Yields:
            ``ConfigFile`` subclasses for which ``version_control_ignored()``
            returns ``True``.
        """
        return (
            cf for cf in cls.concrete_subclasses() if cf().version_control_ignored()
        )

    @classmethod
    def version_controlled_subclasses(cls) -> Generator[type[Self], None, None]:
        """Yield config file classes whose files are tracked by version control.

        Yields:
            ``ConfigFile`` subclasses for which ``version_control_ignored()``
            returns ``False``.
        """
        return (
            cf for cf in cls.concrete_subclasses() if not cf().version_control_ignored()
        )

    @classmethod
    def discard_correct_subclasses(
        cls, subclasses: Iterable[type[Self]]
    ) -> Generator[type[Self], None, None]:
        """Yield only the incorrect config file classes from a collection.

        Used to filter out correct config files when validating a specific
        collection of subclasses.

        Args:
            subclasses: Collection of ``ConfigFile`` subclasses to filter.

        Yields:
            Only the subclasses from the input collection for which ``is_correct()``
            returns ``False``.
        """
        return (cf for cf in subclasses if not cf().is_correct())

    @classmethod
    def sort_key(cls) -> float:
        """Return a sort key that places higher-priority subclasses first.

        Returns the negative of ``priority()`` so that Python's ascending
        sort places subclasses with higher priority values earlier in the list.

        Returns:
            Negative of the subclass priority value.
        """
        # sort by priority (higher first),
        # so return negative priority for ascending sort
        return -cls().priority()

    @classmethod
    @cache
    def configs(cls) -> ConfigT:
        """Return the required configuration structure.

        Delegates to ``_configs()`` and caches the result so that
        ``_configs()`` is only called once per class.

        Returns:
            Minimum required configuration as a dict or list.
        """
        return cls()._configs()  # noqa: SLF001

    @classmethod
    @cache
    def load(cls) -> ConfigT:
        """Load and return the current file contents.

        Delegates to ``_load()`` and caches the result so the file is only
        read once per session. The cache is cleared whenever ``dump()`` is
        called.

        Returns:
            Parsed configuration as a dict or list.
        """
        instance = cls()
        logger.debug("Loading %s", instance)
        return instance._load()

    def validate(self) -> None:
        """Validate the config file, creating or updating it as needed.

        Performs the following steps in order:

        1. Creates the file (and any missing parent directories) if it does
           not exist, then writes ``configs()`` as the initial content.
        2. Returns immediately if the file is already correct.
        3. Merges ``configs()`` into the current file content to fill any
           missing keys while preserving user additions, then writes the result.
        4. Raises ``RuntimeError`` if the file is still not correct after the
           merge, which typically indicates a manual conflict in the file.

        This method is idempotent and safe to call repeatedly.

        Raises:
            RuntimeError: If the file cannot be corrected after merging.
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
        """Create the config file and any missing parent directories.

        Touches the file (creating it empty) after ensuring the full parent
        directory tree exists. Called automatically by ``validate()`` when
        the file is absent.
        """
        path = self.path()
        typer.echo(f"Creating {self}")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()

    def dump(self, configs: ConfigT) -> None:
        """Write configuration to disk and keep the load cache consistent.

        Clears the ``load()`` cache before and after calling ``_dump()`` to
        prevent stale data from being returned if anything reads the cache
        during or after the write.

        Args:
            configs: Configuration data to write.
        """
        typer.echo(f"Updating {self}")
        self.load.cache_clear()
        self._dump(configs)
        self.load.cache_clear()

    def merge_configs(self) -> ConfigT:
        """Merge the required configuration into the current file contents.

        Walks both structures and fills in every key or list item that is
        present in ``configs()`` but absent in ``load()``. Keys that exist
        only in the loaded file are left untouched, preserving user customizations.

        Returns:
            Updated configuration containing both required and existing values.
        """
        return merge_nested_structures(subset=self.configs(), superset=self.load())

    def is_correct(self) -> bool:
        """Return whether the config file passes validation.

        A file is considered correct if it contains at least all the keys and
        values declared in ``configs()`` (additional keys are allowed).

        Returns:
            ``True`` if all required configuration is present in the file.
        """
        return self.is_correct_recursively()

    def is_correct_recursively(self) -> bool:
        """Return whether the required configuration is a subset of the file contents.

        Delegates to ``nested_structure_is_subset`` to recursively verify that
        every key and value in ``configs()`` is present in ``load()``.

        Returns:
            ``True`` if all required keys and values are present in the file.
        """
        return nested_structure_is_subset(self.configs(), self.load())

    def path(self) -> Path:
        """Return the full path to the config file.

        Assembles the path from ``parent_path()``, ``stem()``,
        ``extension_separator()``, and ``extension()``.

        Returns:
            Full path to the config file.
        """
        return self.parent_path() / (
            self.stem() + self.extension_separator() + self.extension()
        )

    def extension_separator(self) -> str:
        """Return the character separating the stem from the extension.

        Returns:
            Always ``"."``.
        """
        return "."

    def priority(self) -> float:
        """Return the validation priority for this config file.

        Higher values cause the file to be validated earlier relative to others.
        Defaults to ``Priority.DEFAULT`` (0). Override in subclasses that must
        be validated before others.

        Returns:
            Validation priority as a float.
        """
        return Priority.DEFAULT

    def version_control_ignored(self) -> bool:
        """Return whether this config file is excluded from version control.

        Files that return ``True`` are excluded from the ``all_config_files_correct``
        session autouse fixture check, since they are not committed to the
        repository. Defaults to ``False`` (tracked by version control).

        Returns:
            ``True`` if the file is git-ignored; ``False`` otherwise.
        """
        return False


class ListConfigFile(ConfigFile[ConfigList]):
    """Abstract base for config files whose content is a list.

    Binds the ``ConfigT`` type parameter to ``ConfigList``, giving subclasses
    properly typed ``load()``, ``dump()``, and ``configs()`` methods.
    """


class DictConfigFile(ConfigFile[ConfigDict]):
    """Abstract base for config files whose content is a dict.

    Binds the ``ConfigT`` type parameter to ``ConfigDict``, giving subclasses
    properly typed ``load()``, ``dump()``, and ``configs()`` methods.
    """
