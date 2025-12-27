"""Directed graph implementation for package dependency analysis.

Provides a DiGraph with bidirectional traversal for analyzing dependency relationships.
"""

from typing import Self

from pyrig.src.modules.class_ import get_cached_instance


class DiGraph:
    """Directed graph with bidirectional traversal.

    Maintains forward and reverse edges for O(1) neighbor lookups.

    Attributes:
        _nodes: All node identifiers.
        _edges: Forward adjacency (node → outgoing neighbors).
        _reverse_edges: Reverse adjacency (node → incoming neighbors).
    """

    @classmethod
    def cached(cls) -> Self:
        """Get cached singleton instance.

        Returns:
            Cached DiGraph instance.
        """
        return get_cached_instance(cls)  # type: ignore[no-any-return, arg-type]

    def __init__(self) -> None:
        """Initialize empty directed graph."""
        self._nodes: set[str] = set()
        self._edges: dict[str, set[str]] = {}  # node -> outgoing neighbors
        self._reverse_edges: dict[str, set[str]] = {}  # node -> incoming neighbors

    def add_node(self, node: str) -> None:
        """Add node to graph.

        Args:
            node: Node identifier.
        """
        self._nodes.add(node)
        if node not in self._edges:
            self._edges[node] = set()
        if node not in self._reverse_edges:
            self._reverse_edges[node] = set()

    def add_edge(self, source: str, target: str) -> None:
        """Add directed edge from source to target.

        Args:
            source: Edge origin (depends on target).
            target: Edge destination (dependency of source).
        """
        self.add_node(source)
        self.add_node(target)
        self._edges[source].add(target)
        self._reverse_edges[target].add(source)

    def __contains__(self, node: str) -> bool:
        """Check if node exists.

        Args:
            node: Node identifier.

        Returns:
            True if node exists.
        """
        return node in self._nodes

    def __getitem__(self, node: str) -> set[str]:
        """Get outgoing neighbors (dependencies) of node.

        Args:
            node: Node identifier.

        Returns:
            Set of dependencies (empty if node doesn't exist).
        """
        return self._edges.get(node, set())

    def nodes(self) -> set[str]:
        """Return all nodes.

        Returns:
            Set of all node identifiers.
        """
        return self._nodes

    def has_edge(self, source: str, target: str) -> bool:
        """Check if directed edge exists.

        Args:
            source: Edge origin.
            target: Edge destination.

        Returns:
            True if edge exists.
        """
        return target in self._edges.get(source, set())

    def ancestors(self, target: str) -> set[str]:
        """Find all nodes that can reach target (transitive dependents).

        Args:
            target: Node to find ancestors for.

        Returns:
            Set of all nodes with path to target (excludes target).
        """
        if target not in self:
            return set()

        visited: set[str] = set()
        queue = list(self._reverse_edges.get(target, set()))

        while queue:
            node = queue.pop(0)
            if node not in visited:
                visited.add(node)
                queue.extend(self._reverse_edges.get(node, set()) - visited)

        return visited

    def shortest_path_length(self, source: str, target: str) -> int:
        """Find shortest path length between nodes.

        Args:
            source: Starting node.
            target: Destination node.

        Returns:
            Number of edges in shortest path (0 if source == target).

        Raises:
            ValueError: If node not in graph or no path exists.
        """
        if source not in self or target not in self:
            msg = f"Node not in graph: {source if source not in self else target}"
            raise ValueError(msg)

        if source == target:
            return 0

        visited: set[str] = {source}
        queue: list[tuple[str, int]] = [(source, 0)]

        while queue:
            node, distance = queue.pop(0)
            for neighbor in self._edges.get(node, set()):
                if neighbor == target:
                    return distance + 1
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, distance + 1))

        msg = f"No path from {source} to {target}"
        raise ValueError(msg)

    def topological_sort_subgraph(self, nodes: set[str]) -> list[str]:
        """Topologically sort subset of nodes (dependencies before dependents).

        Uses Kahn's algorithm. Edge A → B means "A depends on B", so B appears before A.

        Args:
            nodes: Nodes to sort (only edges within this set considered).

        Returns:
            Nodes in topological order (dependencies first).

        Raises:
            ValueError: If subgraph contains cycle.
        """
        # Count outgoing edges (dependencies) for each node in the subgraph
        # Nodes with 0 outgoing edges have no dependencies
        out_degree: dict[str, int] = dict.fromkeys(nodes, 0)

        for node in nodes:
            for dependency in self._edges.get(node, set()):
                if dependency in nodes:
                    out_degree[node] += 1

        # Start with nodes that have no dependencies in the subgraph
        queue = [node for node in nodes if out_degree[node] == 0]
        result: list[str] = []

        while queue:
            # Sort queue for deterministic ordering
            queue.sort()
            node = queue.pop(0)
            result.append(node)

            # For each package that depends on this node (reverse edges)
            for dependent in self._reverse_edges.get(node, set()):
                if dependent in nodes:
                    out_degree[dependent] -= 1
                    if out_degree[dependent] == 0:
                        queue.append(dependent)

        # Check for cycles
        if len(result) != len(nodes):
            msg = "Cycle detected in subgraph, cannot topologically sort"
            raise ValueError(msg)

        return result
