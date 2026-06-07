"""Abstract base for cross-package subclass discovery.

Provides ``DependencySubclass``, an abstract base class that enables
plugin-style extensibility across multiple installed packages without
explicit registration.
"""

import json
import logging
from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator
from functools import cache
from types import ModuleType
from typing import Any, Self, TypeVar, cast

from pyrig.core.introspection.classes import (
    classproperty,
    discard_abstract_classes,
    discard_parent_classes,
)
from pyrig.core.introspection.dependencies import (
    discover_subclasses_across_dependencies,
)

logger = logging.getLogger(__name__)

T = TypeVar("T", bound="DependencySubclass")


class DependencySubclass(ABC):
    """Abstract base for cross-package subclass discovery.

    Concrete subclasses must implement ``dependency_package()`` to declare
    the package where their implementations live. The dependency root is
    inferred automatically from the root package of ``dependency_package()``.
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
    def dependency_package(cls) -> ModuleType:
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

        Convenience shortcut equivalent to ``cls.L()``. The instance is
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
            The resolved leaf subclass type. May be abstract, and may be a
            dynamically synthesized merge of multiple leaves (see ``leaf()``).
        """
        return cls.leaf()

    @classmethod
    def leaf(cls) -> type[Self]:
        """Return the leaf subclass found across dependent packages.

        Discovers every leaf subclass via ``subclasses()`` and resolves
        them to a single class:

        - No subclasses found: returns ``cls`` itself.
        - Exactly one leaf: returns that leaf.
        - Multiple leaves: logs a warning and returns a dynamically created
          subclass that inherits from every leaf. The leaves are ordered by
          ``sort_key()`` so the result is deterministic and earlier-sorted
          leaves take precedence in the method resolution order.
          Cooperative ``super()`` overrides from every leaf are combined;
          genuinely conflicting overrides resolve by MRO order, which is why
          the warning advises defining an explicit merged subclass when the
          overrides interact.

        Returns:
            The resolved leaf subclass. May be abstract. When multiple
            leaves are found, a synthesized subclass combining all of them.
        """
        subclasses = cls.subclasses()
        leaf = next(subclasses, cls)
        second = next(subclasses, None)
        if second is None:
            return leaf

        # Sort for a deterministic MRO: earlier-sorted leaves take precedence.
        leaves = cls.subclasses_sorted([leaf, second, *subclasses])

        logger.warning(
            """Multiple leaf subclasses found for %s: %s.
A subclass with all leaves as parents will be created to resolve this.
Defining multiple leaf subclasses can lead to conflicting behaviour
if their overrides interact with each other in an incompatible way.
This is safe if the overrides do not affect each other, but if they do then
please resolve it yourself by defining your own final subclass with these
leaves as parents and reconciling any conflicts with explicit overrides.
""",
            cls,
            json.dumps([str(subcls) for subcls in leaves], indent=4),
        )

        merged = type(leaves[0].__name__, tuple(leaves), {})
        return cast("type[Self]", merged)

    @classmethod
    def concrete_subclasses(cls) -> Iterator[type[Self]]:
        """Yield all non-abstract subclasses discovered across dependent packages.

        Delegates to ``subclasses()`` and filters out abstract classes. Use
        this when only instantiable implementations are needed.

        Yields:
            Non-abstract subclass types.
        """
        return discard_abstract_classes(cls.subclasses())

    @classmethod
    def subclasses(cls) -> Iterator[type[Self]]:
        """Yield all subclasses discovered across the package ecosystem.

        Searches every installed package that depends on the root package of
        ``dependency_package()``. Intermediate parent classes are discarded,
        leaving only the outermost leaf-level subclasses.

        Yields:
            Subclass types with intermediate parent classes removed.
        """
        return discard_parent_classes(
            discover_subclasses_across_dependencies(
                cls,
                package=cls.dependency_package(),
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
