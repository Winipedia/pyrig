"""Utilities for discovering and ordering subclasses across packages.

This module provides an abstract base `DependencySubclass` that standardizes how
classes discover their concrete implementations across dependent packages.
It centralizes the `definition_package`, `sorting_key`, and discovery helpers
so different subsystems (tools, config files, builders) can share a
consistent discovery API.
"""

from abc import ABC, abstractmethod
from collections.abc import Generator
from functools import cache
from types import ModuleType
from typing import Any, Self, TypeVar

import pyrig
from pyrig.src.iterate import generator_has_items
from pyrig.src.modules.class_ import (
    classproperty,
    discard_abstract_classes,
    discard_parent_classes,
)
from pyrig.src.modules.package import (
    discover_subclasses_across_dependents,
)

T = TypeVar("T", bound="DependencySubclass")


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

        Must be overridden by each subclass to specify its own package.

        Returns:
            Package module containing the concrete subclass definitions.
        """

    @classmethod
    @abstractmethod
    def sorting_key(cls, subclass: type[T]) -> Any:
        """Return a sort key for the given subclass.

        This key is used when ordering discovered subclasses. Implementations
        should return a value that sorts subclasses in the intended order
        (for example, by priority or by name).

        Args:
            subclass: The subclass to compute a key for.

        Returns:
            A value suitable for use as a sort key.
        """

    @classmethod
    def base_dependency(cls) -> ModuleType:
        """Return the base dependency module for this subclass.

        This is used to discover subclasses across dependent packages.

        Returns:
            The base dependency module.
        """
        return pyrig

    @classmethod
    @cache
    def sorted_subclasses(cls) -> tuple[type[Self], ...]:
        """Discover and return all concrete subclasses, sorted by sorting key.

        Discovers all non-abstract subclasses across dependent packages, scoped to
        the definition package. Returns them as a tuple sorted by the value
        returned from `sorting_key()`.

        Returns:
            Tuple of concrete subclass types, sorted by sorting key.
        """
        return tuple(sorted(cls.subclasses(), key=cls.sorting_key))

    @classmethod
    def subclasses(cls) -> Generator[type[Self], None, None]:
        """Discover all non-abstract subclasses.

        Search all dependent packages of the base dependency, scoped to the
        definition package, and return the results sorted by `sorting_key`.

        Returns:
            Sorted tuple of concrete subclass types.
        """
        return discard_parent_classes(
            discard_abstract_classes(
                discover_subclasses_across_dependents(
                    cls,
                    dep=cls.base_dependency(),
                    load_package_before=cls.definition_package(),
                )
            )
        )

    @classproperty
    @cache  # noqa: B019  # false warning bc of custom classproperty decorator
    def L(cls: type[Self]) -> type[Self]:  # noqa: N802, N805
        """Get the final leaf subclass (deepest in the inheritance tree).

        Returns:
            Final leaf subclass type. Can be abstract.

        See Also:
            subclasses: Discover all concrete subclasses, sorted by sorting key.
        """
        has_leaf, subclasses = generator_has_items(cls.subclasses())

        if not has_leaf:
            msg = f"No concrete subclasses found for {cls.__name__}"
            raise TypeError(msg)

        leaf = next(subclasses)
        second = next(subclasses, None)
        if second is not None:
            msg = (
                f"Multiple concrete subclasses found for {cls.__name__}: "
                f"{', '.join(c.__name__ for c in (leaf, second, *subclasses))}"
            )
            raise TypeError(msg)
        return leaf

    @classproperty
    @cache  # noqa: B019  # false warning bc of custom classproperty decorator
    def I(cls: type[Self]) -> Self:  # noqa: E743, N802, N805
        """Get an instance of the final leaf subclass."""
        return cls.L()
