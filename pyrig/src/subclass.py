"""Utilities for discovering and ordering subclasses across packages.

This module provides an abstract base `DependencySubclass` that standardizes how
classes discover their concrete implementations across dependent packages.
It centralizes the `definition_package`, `sorting_key`, and discovery helpers
so different subsystems (tools, config files, builders) can share a
consistent discovery API.
"""

from abc import ABC, abstractmethod
from types import ModuleType
from typing import Any, Self

import pyrig
from pyrig.src.modules.class_ import classproperty
from pyrig.src.modules.package import (
    discover_leaf_subclass_across_dependents,
    discover_subclasses_across_dependents,
)
from pyrig.src.singleton import Singleton


class DependencySubclass(ABC):
    """Abstract base providing a subclass-discovery contract.

    Subclasses must implement `definition_package()` to indicate the package
    where implementations live, and `sorting_key()` to provide a stable sort
    key for ordering discovered subclasses.
    """

    @classmethod
    @abstractmethod
    def definition_package(cls) -> ModuleType:
        """Get the package where this class's subclasses are defined.

        Should be overridden by subclasses to specify their own package.

        Returns:
            Package module containing the concrete subclass definitions.
        """

    @classmethod
    @abstractmethod
    def sorting_key[S: DependencySubclass](cls, subclass: type[S]) -> Any:
        """Return a sort key for the given subclass.

        This key is used when ordering discovered subclasses. Implementations
        should return a value that sorts subclasses in the intended order
        (for example, by priority or by name).

        Args:
            subclass (type[S]): The subclass to compute a key for.

        Returns:
            Any: A value suitable for use as a sort key.
        """

    @classmethod
    def base_dependency(cls) -> ModuleType:
        """Returns the base dependency module for this subclass.

        This is used to discover subclasses across dependent packages.

        Returns:
            The base dependency module.
        """
        return pyrig

    @classmethod
    def subclasses(cls) -> list[type[Self]]:
        """Discover all non-abstract subclasses.

        Discovers all non-abstract subclasses of this class across dependent
        packages of the base dependency, scoped to the definition package,
        and returns them sorted by ``sorting_key``.

        Returns:
            Sorted list of concrete subclass types.
        """
        return sorted(
            discover_subclasses_across_dependents(
                cls,
                cls.base_dependency(),
                cls.definition_package(),
                discard_parents=True,
                exclude_abstract=True,
            ),
            key=cls.sorting_key,
        )

    @classproperty
    def L(cls) -> type[Self]:  # noqa: N802, N805
        """Get the final leaf subclass (deepest in the inheritance tree).

        Returns:
            Final leaf subclass type. Can be abstract.

        See Also:
            subclasses: Get all subclasses regardless of priority
        """
        return discover_leaf_subclass_across_dependents(
            cls=cls,
            dep=cls.base_dependency(),
            load_package_before=cls.definition_package(),
        )

    @classproperty
    def I(cls) -> Self:  # noqa: E743, N802, N805
        """Get an instance of the final leaf subclass."""
        return cls.L()


class SingletonDependencySubclass(Singleton, DependencySubclass):
    """Convenience base combining `Singleton` with `DependencySubclass`.

    By inheriting from `Singleton`, the inherited ``I`` property returns a
    cached singleton instance of the leaf subclass instead of creating a new
    one on every access.
    """
