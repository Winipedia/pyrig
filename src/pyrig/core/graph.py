"""Generic directed graph with bidirectional edge traversal.

Maintains forward and reverse adjacency mappings to support efficient traversal
in both directions: from a node to its outgoing neighbors (dependencies) and
from a node to all nodes that transitively point to it (ancestors).
"""

import heapq
from abc import ABC, abstractmethod
from collections import deque


class DiGraph(ABC):
    """Abstract base class for a directed graph with bidirectional edge traversal.

    Maintains forward and reverse adjacency mappings, enabling O(1) neighbor
    lookups in either direction: outgoing neighbors via ``__getitem__`` and
    incoming neighbors (all nodes that can reach a given node) via ``ancestors``.

    Subclasses must implement ``build`` to populate the graph at construction
    time. If a ``root`` node is provided, the graph is automatically pruned after
    building to retain only that node and all nodes that transitively point to it.
    """

    def __init__(self, root: str | None = None) -> None:
        """Initialize and build the graph structure.

        Args:
            root: If provided, prune the graph after building to keep only
                this node and nodes that depend on it (ancestors).
        """
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

        Called automatically during ``__init__`` before any optional pruning.
        Subclasses must implement this method to define the graph structure
        using ``add_node`` and ``add_edge``.
        """

    def prune(self, root: str) -> None:
        """Remove all nodes that do not depend on root.

        Keeps ``root`` and all its ancestors (nodes with a directed path to
        ``root``). All other nodes and their associated edges are removed.
        Rebuilds the internal data structures from the kept set in a single
        pass, which is more efficient than removing nodes one at a time.

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
        """Check whether a node exists in the graph.

        Args:
            node: Node identifier to look up.

        Returns:
            ``True`` if the node is present, ``False`` otherwise.
        """
        return node in self._nodes

    def __getitem__(self, node: str) -> set[str]:
        """Get the outgoing neighbors of a node.

        Args:
            node: Node identifier.

        Returns:
            Set of nodes that this node points to (empty set if node doesn't exist).
        """
        return self._edges.get(node, set())

    def nodes(self) -> set[str]:
        """Return all node identifiers in the graph.

        Returns:
            Set of every node currently in the graph.
        """
        return self._nodes

    def has_edge(self, source: str, target: str) -> bool:
        """Check whether a directed edge exists from source to target.

        Args:
            source: The origin node.
            target: The destination node.

        Returns:
            ``True`` if the edge exists, ``False`` if either node is absent
            or no edge connects them.
        """
        return target in self._edges.get(source, set())

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

        Performs a BFS over reverse edges to collect every node that can reach
        the target directly or transitively. The target itself is excluded from
        the result.

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

        Uses Kahn's algorithm with a min-heap to produce a deterministic result
        when multiple nodes are ready to be emitted at the same step. An edge
        A → B means "A depends on B", so B appears before A in the output.

        Only edges whose both endpoints are in ``nodes`` are considered; edges
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
