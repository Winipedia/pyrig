"""Dependency graph of installed Python packages.

Defines the ``DependencyGraph`` class, which builds a directed graph of
installed Python packages and their dependencies using
``importlib.metadata``. Provides methods to query which packages depend
on a given package, facilitating pyrig's multi-package discovery system.
"""

import importlib.metadata
import logging
from types import ModuleType

from pyrig.src.graph import DiGraph
from pyrig.src.modules.module import import_modules
from pyrig.src.singleton import Singleton
from pyrig.src.string_ import package_req_name_split_pattern

logger = logging.getLogger(__name__)


class DependencyGraph(DiGraph, Singleton):
    """Directed graph of installed Python package dependencies.

    Nodes are package names, edges represent dependency relationships.
    Built automatically on first instantiation by scanning installed distributions.
    As a ``Singleton``, the graph is constructed once and shared across the
    application for the lifetime of the process.
    Central to pyrig's multi-package discovery system.
    """

    def build(self) -> None:
        """Build the graph from installed Python distributions."""
        logger.debug("Building dependency graph from installed distributions")
        for dist in importlib.metadata.distributions():
            name, deps = self.parse_name_and_deps_from_raw_metadata(dist)
            if name:
                self.add_node(name)
                for dep in deps:
                    self.add_edge(name, dep)  # package → dependency
        logger.debug("Dependency graph built with %d packages", len(self.nodes()))

    @staticmethod
    def parse_name_and_deps_from_raw_metadata(
        dist: importlib.metadata.Distribution,
    ) -> tuple[str, list[str]]:
        """Extract package name and dependencies from raw distribution metadata.

        Parses the ``METADATA`` file directly as plain text instead of using
        ``dist.metadata`` or ``dist.requires``, which internally delegate to
        Python's ``email.message_from_string()``. The ``email.parser`` module
        implements full RFC 2822 header parsing — designed for email messages —
        and is significantly slower than the simple line-based extraction needed
        here, where we only care about ``Name:`` and ``Requires-Dist:`` headers.

        The ``METADATA`` file follows the
        `Core Metadata specification <https://packaging.python.org/en/latest/specifications/core-metadata/>`_
        with a simple ``Key: Value`` format (one header per line). ``Name``
        always appears exactly once. ``Requires-Dist`` appears zero or more
        times, each listing one dependency requirement string.

        Args:
            dist: Distribution object to extract metadata from.

        Returns:
            Tuple of (normalized_name, list_of_normalized_dependency_names).
            Name is empty string if not found. Dependencies list may be empty.
        """
        text = dist.read_text("METADATA") or ""
        name = ""
        deps: list[str] = []
        for line in text.splitlines():
            if line.startswith("Name: "):
                name = DependencyGraph.normalize_package_name(line[6:])
            elif line.startswith("Requires-Dist: "):
                dep = DependencyGraph.parse_package_name_from_req(line[15:])
                if dep:
                    deps.append(dep)
        return name, deps

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
    def parse_package_name_from_req(req: str) -> str | None:
        """Extract package name from a requirement string.

        Uses ``pyrig.src.string_.package_req_name_split_pattern`` to split the
        requirement string at the first non-name character.

        Args:
            req: Requirement string (e.g., "requests>=2.0,<3.0").

        Returns:
            Normalized package name, or None if parsing fails.
        """
        # Split on the first non-alphanumeric character (except -, _, and .)
        # Uses module-level compiled pattern for performance
        dep = package_req_name_split_pattern().split(req.strip(), maxsplit=1)[0].strip()
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

        return import_modules(dependents)
