"""Abstract directed graph foundation with forward and reverse edge traversal."""

import heapq
from abc import ABC, abstractmethod
from collections import deque
from functools import cache
from typing import Any, Self


class DiGraph(ABC):
    """Abstract directed graph with forward and reverse adjacency tracking.

    Subclasses implement `build` to populate nodes and edges. At construction,
    `build` is called first; if a `root` node is given, the graph is then pruned
    to retain only that node and every node that transitively points to it.
    """

    @classmethod
    @cache
    def cached(cls, *args: Any, **kwargs: Any) -> Self:
        """Return a cached instance, constructing it only on the first call.

        Repeated calls with identical arguments return the same instance
        without rebuilding the graph.

        Args:
            *args: Positional arguments forwarded to the constructor.
            **kwargs: Keyword arguments forwarded to the constructor.

        Returns:
            The cached graph instance for the given arguments.
        """
        return cls(*args, **kwargs)

    def __init__(self, root: str | None = None) -> None:
        """Build the graph, then prune it to `root` if one is given."""
        self.root = root
        self._nodes: set[str] = set()
        self._edges: dict[str, set[str]] = {}  # node -> outgoing neighbors
        self._reverse_edges: dict[str, set[str]] = {}  # node -> incoming neighbors
        self.build()
        if self.root is not None:
            self.prune(self.root)

    @abstractmethod
    def build(self) -> None:
        """Populate the graph with nodes and edges.

        Called automatically during construction before any optional pruning.
        Implementations use `add_node` and `add_edge` to define the graph
        structure.
        """

    def prune(self, root: str) -> None:
        """Remove all nodes that are neither root nor an ancestor of root.

        Keeps `root` and all its ancestors (nodes with a directed path to
        `root`). All other nodes and their associated edges are removed.

        Args:
            root: The root node to prune around.
        """
        keep = self.ancestors(root) | {root}
        self._nodes = keep
        self._edges = {n: self._edges[n] & keep for n in keep}
        self._reverse_edges = {n: self._reverse_edges[n] & keep for n in keep}

    def add_edge(self, source: str, target: str) -> None:
        """Add a directed edge from source to target.

        Creates both nodes if they do not already exist.

        Args:
            source: Edge origin node.
            target: Edge destination node.
        """
        self.add_node(source)
        self.add_node(target)
        self._edges[source].add(target)
        self._reverse_edges[target].add(source)

    def add_node(self, node: str) -> None:
        """Add a node to the graph. No-op if the node already exists.

        Args:
            node: Node identifier to add.
        """
        self._nodes.add(node)
        if node not in self._edges:
            self._edges[node] = set()
        if node not in self._reverse_edges:
            self._reverse_edges[node] = set()

    def __contains__(self, node: str) -> bool:
        """Check whether a node exists in the graph."""
        return node in self._nodes

    def __getitem__(self, node: str) -> set[str]:
        """Return the outgoing neighbors of a node, or an empty set if absent.

        Args:
            node: Node identifier.

        Returns:
            Set of nodes that `node` has a directed edge to.
        """
        return self._edges.get(node, set())

    def nodes(self) -> set[str]:
        """Return all node identifiers currently in the graph."""
        return self._nodes

    def sorted_ancestors(self, target: str) -> list[str]:
        """Return all ancestors of the target node sorted in topological order.

        Ancestors are nodes that have a directed path to the target (i.e., nodes
        that depend on it directly or transitively). The result is sorted so that
        dependencies appear before their dependents.

        Args:
            target: Node to find ancestors of.

        Returns:
            List of ancestor node identifiers, with dependencies first.
            Returns an empty list if the target is not in the graph.

        Raises:
            RuntimeError: If the ancestor subgraph contains a cycle, making
                topological sorting impossible.
        """
        return self.topological_sort_subgraph(self.ancestors(target))

    def ancestors(self, target: str) -> set[str]:
        """Find all nodes that have a directed path to the target node.

        Collects every node that reaches the target directly or transitively.
        The target itself is excluded from the result.

        Args:
            target: Node to find ancestors for.

        Returns:
            Set of all nodes with a directed path to the target, excluding the
            target itself. Returns an empty set if the target is not in the graph.
        """
        visited: set[str] = set()
        queue: deque[str] = deque(self._reverse_edges.get(target, set()))

        while queue:
            node = queue.popleft()
            if node not in visited:
                visited.add(node)
                # Iterate directly to avoid creating intermediate set
                for neighbor in self._reverse_edges.get(node, set()):
                    if neighbor not in visited:
                        queue.append(neighbor)

        return visited

    def topological_sort_subgraph(self, nodes: set[str]) -> list[str]:
        """Sort a subset of nodes in topological order.

        An edge A → B means "A depends on B", so B appears before A in the
        output. The ordering is deterministic: when multiple nodes are ready to
        be emitted at the same step, they are emitted in ascending order.

        Only edges whose both endpoints are in `nodes` are considered; edges
        to or from nodes outside the subset are ignored.

        Args:
            nodes: The subset of nodes to sort.

        Returns:
            List of nodes in topological order, with each node's dependencies
            appearing before the node itself.

        Raises:
            RuntimeError: If the subgraph contains a cycle, making topological
                sorting impossible.
        """
        # Count outgoing edges (dependencies) for each node in the subgraph
        # Nodes with 0 outgoing edges have no dependencies
        out_degree: dict[str, int] = dict.fromkeys(nodes, 0)

        for node in nodes:
            for dependency in self._edges.get(node, set()):
                if dependency in nodes:
                    out_degree[node] += 1

        # Use heapq for O(log n) insertion maintaining sorted order
        # This replaces O(n log n) sort() + O(n) pop(0) with O(log n) heappop()
        heap: list[str] = [node for node in nodes if out_degree[node] == 0]
        heapq.heapify(heap)
        result: list[str] = []

        while heap:
            node = heapq.heappop(heap)
            result.append(node)

            # For each package that depends on this node (reverse edges)
            for dependent in self._reverse_edges.get(node, set()):
                if dependent in nodes:
                    out_degree[dependent] -= 1
                    if out_degree[dependent] == 0:
                        heapq.heappush(heap, dependent)

        # Check for cycles
        if len(result) != len(nodes):
            msg = (
                "Graph contains a cycle; topological sort not possible. "
                "This indicates a circular dependency among the following nodes: "
                f"{set(nodes) - set(result)}"
            )
            raise RuntimeError(msg)

        return result
