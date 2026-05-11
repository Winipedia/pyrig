"""Dependency graph of installed Python packages.

Builds and queries a directed graph of installed package dependency
relationships to support cross-package discovery in the pyrig ecosystem.
"""

import importlib.metadata
import logging
from collections.abc import Generator

from pyrig.core.graph import DiGraph
from pyrig.core.strings import (
    dependency_requirement_as_package_name,
)

logger = logging.getLogger(__name__)


class DependencyGraph(DiGraph):
    """Directed graph of installed Python package dependencies.

    Nodes are package names; an edge A → B means "A depends on B".
    The graph is built automatically at instantiation by scanning all
    installed distributions via ``importlib.metadata``.

    When a ``root`` package is given, the graph is pruned to contain only
    that package and every package that depends on it (directly or
    transitively). This is the primary usage in pyrig's multi-package
    discovery system.
    """

    def __init__(self, root: str | None = None) -> None:
        """Initialize the dependency graph rooted at the given package.

        Only ``root`` itself and packages that depend on it (directly or
        transitively) are included in the graph after pruning.

        Args:
            root: Name of the root package to build the graph around.
        """
        super().__init__(
            root=dependency_requirement_as_package_name(root) if root else None
        )

    def build(self) -> None:
        """Build the graph from installed Python distributions."""
        logger.debug("Building dependency graph from installed distributions")
        for dist in importlib.metadata.distributions():
            name, deps = self.parse_name_and_deps(dist)
            if name:
                self.add_node(name)
                for dep in deps:
                    self.add_edge(name, dep)  # package → dependency
        logger.debug("Dependency graph built with %d packages", len(self.nodes()))

    def parse_name_and_deps(
        self, dist: importlib.metadata.Distribution
    ) -> tuple[str, Generator[str, None, None]]:
        """Extract the package name and dependencies from a distribution.

        Reads the package name from ``dist.name`` and constructs a lazy
        generator of normalized dependency names from ``dist.requires``.

        Args:
            dist: Distribution object to extract metadata from.

        Returns:
            A two-tuple of ``(normalized_name, deps_generator)`` where
            ``normalized_name`` is the normalized package name and ``deps_generator``
            is a generator that yields normalized names of each declared dependency
            (yields nothing if the package declares no dependencies).
        """
        return dependency_requirement_as_package_name(dist.name), (
            dependency_requirement_as_package_name(req) for req in (dist.requires or [])
        )
