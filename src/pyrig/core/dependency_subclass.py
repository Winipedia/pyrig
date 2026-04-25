"""Abstract base for cross-package subclass discovery.

Provides ``DependencySubclass``, an abstract base class that enables
plugin-style extensibility across multiple installed packages without
explicit registration.
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
    """Abstract base for cross-package subclass discovery.

    Concrete subclasses must implement ``definition_package()`` to declare
    the package where their implementations live, and ``base_dependency()``
    to declare the base installed package whose dependents are searched.
    The optional ``sort_key()`` hook controls ordering in
    ``subclasses_sorted()``.

    This class is the foundation of pyrig's plugin architecture. Any
    subsystem that needs to discover its implementations across installed
    dependent packages — tools, config files, builders — should inherit
    from this class, either directly or through a shared intermediate such
    as ``RigDependencySubclass``.
    """

    def __str__(self) -> str:
        """Return the fully qualified class name of this instance.

        Combines the module path with the class name to produce a string
        such as ``myapp.rig.configs.MyConfigFile``. Useful where an
        unambiguous identifier is needed for display or logging.

        Returns:
            Dotted module path and class name joined with a period.
        """
        return f"{self.__module__}.{self.__class__.__name__}"

    @classmethod
    @abstractmethod
    def definition_package(cls) -> ModuleType:
        """Return the package where this class's implementations are defined.

        Used by ``subclasses()`` to scope cross-package discovery to the
        correct namespace. For example, a ``ConfigFile`` subclass returns
        its ``configs`` package so that only config-related modules are
        searched across dependents.

        Must be overridden by each concrete subclass.

        Returns:
            Package module that contains the concrete subclass definitions.
        """

    @classmethod
    @abstractmethod
    def base_dependency(cls) -> ModuleType:
        """Return the installed package that anchors the dependency search.

        Used by ``subclasses()`` to find all installed packages that depend
        on this module. For example, returning ``pyrig`` causes discovery to
        search every installed package that lists ``pyrig`` as a dependency.

        Must be overridden by each concrete subclass.

        Returns:
            The base dependency module (e.g. ``pyrig``).
        """

    @classmethod
    def sort_key(cls) -> Any:
        """Return a stable sort key for this subclass.

        Called by ``subclasses_sorted()`` for each subclass in the
        collection. Override to sort by priority, numeric position, or any
        other criterion. The default returns the class name, giving
        alphabetical ordering.

        Returns:
            A value comparable by ``sorted()``.
        """
        return cls.__name__

    @classproperty
    @cache  # noqa: B019  # false warning bc of custom classproperty decorator
    def I(cls) -> Self:  # noqa: E743, N802, N805
        """Return a cached instance of the leaf subclass.

        Convenience shortcut equivalent to ``cls.L()()``. The instance is
        created once per class and reused on every subsequent access.

        Returns:
            Instance of the leaf subclass.
        """
        return cls.L()

    @classproperty
    @cache  # noqa: B019  # false warning bc of custom classproperty decorator
    def L(cls) -> type[Self]:  # noqa: N802, N805
        """Return the cached leaf subclass.

        Convenience shortcut for ``cls.leaf()`` with caching applied so
        that repeated accesses do not re-run the discovery.

        Returns:
            The single leaf subclass type. May be abstract.

        Raises:
            RuntimeError: If more than one leaf subclass is found.
        """
        return cls.leaf()

    @classmethod
    def leaf(cls) -> type[Self]:
        """Return the single leaf subclass found across dependent packages.

        Expects exactly one result from ``subclasses()``. If no subclasses
        are found the class itself is returned. Raises ``RuntimeError`` if
        multiple subclasses are found, because a "leaf" must be
        unambiguous: exactly one active implementation is allowed.

        Returns:
            The sole leaf subclass type. May be abstract.

        Raises:
            RuntimeError: If more than one subclass is discovered across
                the dependent packages.
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

    @classmethod
    def concrete_subclasses(cls) -> Generator[type[Self], None, None]:
        """Yield all non-abstract subclasses discovered across dependent packages.

        Delegates to ``subclasses()`` and filters out abstract classes. Use
        this when only instantiable implementations are needed.

        Yields:
            Non-abstract subclass types in dependency order.
        """
        return discard_abstract_classes(cls.subclasses())

    @classmethod
    def subclasses(cls) -> Generator[type[Self], None, None]:
        """Yield all subclasses discovered across the package ecosystem.

        Searches every installed package that depends on
        ``base_dependency()``, scoped to the module namespace of
        ``definition_package()``. Intermediate parent classes are discarded,
        leaving only the outermost leaf-level subclasses. Results are yielded
        in topological dependency order (base package classes first,
        dependents after).

        Yields:
            Subclass types with intermediate parent classes removed, in
            dependency order.
        """
        return discard_parent_classes(
            discover_subclasses_across_dependents(
                cls,
                dependency=cls.base_dependency(),
                package=cls.definition_package(),
            )
        )

    @classmethod
    def subclasses_sorted(cls, subclasses: Iterable[type[Self]]) -> list[type[Self]]:
        """Sort the given subclasses using each subclass's ``sort_key()``.

        Does not perform any discovery. Pass the output of ``subclasses()``
        or any other iterable of subclass types to produce a
        deterministically ordered list.

        Args:
            subclasses: Subclass types to sort.

        Returns:
            The same subclass types sorted by their ``sort_key()``.
        """
        return sorted(subclasses, key=lambda subclass: subclass.sort_key())
