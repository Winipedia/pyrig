"""Dependency graph of installed Python packages.

This module defines the DependencyGraph class,
which builds a directed graph of installed Python packages
and their dependencies using importlib.metadata.
It provides methods to query which packages depend on a given package,
facilitating pyrig's multi-package discovery system.
"""

import importlib.metadata
import logging
from collections.abc import Iterable
from types import ModuleType

from pyrig.src.graph import DiGraph
from pyrig.src.modules.module import import_module_with_default
from pyrig.src.string_ import pkg_req_name_split_pattern

logger = logging.getLogger(__name__)


class DependencyGraph(DiGraph):
    """Directed graph of installed Python package dependencies.

    Nodes are package names, edges represent dependency relationships.
    Built automatically on instantiation by scanning installed distributions.
    Central to pyrig's multi-package discovery system.
    """

    def __init__(self) -> None:
        """Initialize and build the dependency graph from installed distributions."""
        super().__init__()
        self.build()

    def build(self) -> None:
        """Build the graph from installed Python distributions."""
        logger.debug("Building dependency graph from installed distributions")
        for dist in importlib.metadata.distributions():
            name = self.parse_distname_from_metadata(dist)
            self.add_node(name)

            requires = dist.requires or []
            for req in requires:
                dep = self.parse_pkg_name_from_req(req)
                if dep:
                    self.add_edge(name, dep)  # package → dependency
        logger.debug("Dependency graph built with %d packages", len(self.nodes()))

    @staticmethod
    def parse_distname_from_metadata(dist: importlib.metadata.Distribution) -> str:
        """Extract and normalize distribution name from metadata.

        Args:
            dist: Distribution object.

        Returns:
            Normalized package name (lowercase, underscores).
        """
        # replace - with _ to handle packages like pyrig
        name: str = dist.metadata["Name"]
        return DependencyGraph.normalize_package_name(name)

    @staticmethod
    def all_dependencies() -> list[str]:
        """Get all installed package names.

        Returns:
            List of normalized package names.
        """
        dists = importlib.metadata.distributions()
        # extract the name from the metadata
        return [DependencyGraph.parse_distname_from_metadata(dist) for dist in dists]

    @staticmethod
    def normalize_package_name(name: str) -> str:
        """Normalize a package name (lowercase, hyphens → underscores).

        Args:
            name: Package name to normalize.

        Returns:
            Normalized package name.
        """
        return name.lower().replace("-", "_").strip()

    @staticmethod
    def parse_pkg_name_from_req(req: str) -> str | None:
        """Extract package name from a requirement string.

        Uses pre-compiled regex for better performance when parsing many requirements.

        Args:
            req: Requirement string (e.g., "requests>=2.0,<3.0").

        Returns:
            Normalized package name, or None if parsing fails.
        """
        # Split on the first non-alphanumeric character (except -, _, and .)
        # Uses module-level compiled pattern for performance
        dep = pkg_req_name_split_pattern().split(req.strip(), maxsplit=1)[0].strip()
        return DependencyGraph.normalize_package_name(dep) if dep else None

    def all_depending_on(
        self, package: ModuleType | str, *, include_self: bool = False
    ) -> list[ModuleType]:
        """Find all packages that depend on the given package.

        Primary method for discovering packages that extend pyrig's functionality.

        Args:
            package: Package to find dependents of (module or name string).
            include_self: If True, includes the target package in results.

        Returns:
            List of imported module objects for dependent packages.
            Sorted in topological order (dependencies before dependents).

        Raises:
            ValueError: If package not found in dependency graph.

        Note:
            Only returns packages that can be successfully imported.
        """
        # replace - with _ to handle packages like pyrig
        if isinstance(package, ModuleType):
            package = package.__name__
        target = package.lower()
        if target not in self:
            msg = f"""Package '{target}' not found in dependency graph."""
            raise ValueError(msg)

        dependents_set = self.ancestors(target)
        if include_self:
            dependents_set.add(target)

        # Sort in topological order (dependencies before dependents)
        dependents = self.topological_sort_subgraph(dependents_set)

        logger.debug("Found packages depending on %s: %s", package, dependents)

        return self.import_packages(dependents)

    @staticmethod
    def import_packages(names: Iterable[str]) -> list[ModuleType]:
        """Import packages by name, skipping import failures.

        Args:
            names: Package names to import.

        Returns:
            List of successfully imported modules.
        """
        modules: list[ModuleType] = []
        for name in names:
            module = import_module_with_default(name)
            if module is not None:
                modules.append(module)
        return modules
