"""Utilities for discovering and ordering subclasses across packages.

This module provides an abstract base `DependencySubclass` that standardizes how
classes discover their concrete implementations across dependent packages.
It centralizes the `definition_package`, `sorting_key`, and discovery helpers
so different subsystems (tools, config files, builders) can share a
consistent discovery API.
"""

import json
from abc import ABC, abstractmethod
from collections.abc import Generator, Iterable
from functools import cache
from types import ModuleType
from typing import Any, Self, TypeVar

from pyrig.core.introspection.classes import (
    classproperty,
    discard_abstract_classes,
    discard_parent_classes,
)
from pyrig.core.introspection.dependencies import (
    discover_subclasses_across_dependents,
)

T = TypeVar("T", bound="DependencySubclass")


class DependencySubclass(ABC):
    """Abstract base providing a subclass-discovery contract.

    Subclasses must implement `definition_package()` to indicate the package
    where implementations live, and `sorting_key()` to provide a stable sort
    key for ordering discovered subclasses.
    """

    def __str__(self) -> str:
        """String representation of the class.

        Adds the dotted module name to the class name for clarity
        regarding the dependency context of the class.
        """
        return f"{self.__module__}.{self.__class__.__name__}"

    @classmethod
    @abstractmethod
    def definition_package(cls) -> ModuleType:
        """Get the package where this class's subclasses are defined.

        Must be overridden by each subclass to specify its own package.

        Returns:
            Package module containing the concrete subclass definitions.
        """

    @classmethod
    @abstractmethod
    def base_dependency(cls) -> ModuleType:
        """Return the base dependency module for this subclass.

        This is used to discover subclasses across dependent packages.

        Returns:
            The base dependency module.
        """

    @classmethod
    def sorting_key(cls) -> Any:
        """Return a sort key for the given subclass.

        This key is used when ordering discovered subclasses. Implementations
        should return a value that sorts subclasses in the intended order
        (for example, by priority or by name).

        Default implementation returns the subclass's name, providing a stable
        alphabetical ordering.

        Args:
            subclass: The subclass to compute a key for.

        Returns:
            A value suitable for use as a sort key for builtin: sorted
        """
        return cls.__name__

    @classmethod
    def subclasses_sorted(cls, subclasses: Iterable[type[Self]]) -> list[type[Self]]:
        """Discover and return all concrete subclasses, sorted by sorting key.

        Sorts the given subclasses using the `sorting_key` method.
        This is used to order the results of `subclasses()`.

        Returns:
            List of concrete subclass types, sorted by sorting key.
        """
        return sorted(subclasses, key=lambda subclass: subclass.sorting_key())

    @classmethod
    def concrete_subclasses(cls) -> Generator[type[Self], None, None]:
        """Discover and return all concrete subclasses."""
        return discard_abstract_classes(cls.subclasses())

    @classmethod
    def subclasses(cls) -> Generator[type[Self], None, None]:
        """Discover all subclasses.

        Search all dependent packages of the base dependency, scoped to the
        definition package, and return the results sorted by `sorting_key`.

        Returns:
            Sorted tuple of subclass types.
        """
        return discard_parent_classes(
            discover_subclasses_across_dependents(
                cls,
                dependency=cls.base_dependency(),
                package=cls.definition_package(),
            )
        )

    @classmethod
    def leaf(cls) -> type[Self]:
        """Get the final leaf subclass (deepest in the inheritance tree).

        Returns:
            Final leaf subclass type. Can be abstract.

        See Also:
            subclasses: Discover all concrete subclasses, sorted by sorting key.
        """
        subclasses = cls.subclasses()
        leaf = next(subclasses, cls)
        second = next(subclasses, None)
        if second is None:
            return leaf

        msg = f"""Multiple leaf subclasses found for {cls}.
Defining multiple leaf subclasses is ambiguous.
This can happen if more than one leaf subclass is defined
across all the dependent packages.

Found subclasses:
{json.dumps([str(subcls) for subcls in (leaf, second, *subclasses)], indent=4)}"""
        raise RuntimeError(msg)

    @classproperty
    @cache  # noqa: B019  # false warning bc of custom classproperty decorator
    def L(cls) -> type[Self]:  # noqa: N802, N805
        """Get the final leaf subclass (deepest in the inheritance tree).

        Returns:
            Final leaf subclass type. Can be abstract.

        See Also:
            subclasses: Discover all concrete subclasses, sorted by sorting key.
        """
        return cls.leaf()

    @classproperty
    @cache  # noqa: B019  # false warning bc of custom classproperty decorator
    def I(cls) -> Self:  # noqa: E743, N802, N805
        """Get an instance of the final leaf subclass."""
        return cls.L()
