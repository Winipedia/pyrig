"""Directed graph implementation for dependency analysis.

This module provides a simple but efficient directed graph (DiGraph) data structure
used primarily for analyzing Python package dependency relationships. The graph
supports bidirectional traversal, enabling both "what does X depend on" and
"what depends on X" queries.

The implementation maintains both forward and reverse edge mappings for O(1)
neighbor lookups in either direction, at the cost of doubled memory for edges.

Example:
    >>> graph = DiGraph()
    >>> graph.add_edge("app", "library")
    >>> graph.add_edge("library", "utils")
    >>> graph.ancestors("utils")  # What depends on utils?
    {'app', 'library'}
"""


class DiGraph:
    """A directed graph with efficient bidirectional traversal.

    This graph implementation maintains both forward edges (node -> dependencies)
    and reverse edges (node -> dependents) to support efficient queries in both
    directions. It is designed for package dependency analysis where you often
    need to find all packages that depend on a given package.

    Attributes:
        _nodes: Set of all node identifiers in the graph.
        _edges: Forward adjacency mapping (node -> set of outgoing neighbors).
        _reverse_edges: Reverse adjacency mapping (node -> set of incoming neighbors).

    Example:
        >>> g = DiGraph()
        >>> g.add_edge("A", "B")  # A depends on B
        >>> g.add_edge("A", "C")  # A depends on C
        >>> g["A"]  # What does A depend on?
        {'B', 'C'}
        >>> g.ancestors("B")  # What depends on B?
        {'A'}
    """

    def __init__(self) -> None:
        """Initialize an empty directed graph with no nodes or edges."""
        self._nodes: set[str] = set()
        self._edges: dict[str, set[str]] = {}  # node -> outgoing neighbors
        self._reverse_edges: dict[str, set[str]] = {}  # node -> incoming neighbors

    def add_node(self, node: str) -> None:
        """Add a node to the graph if it doesn't already exist.

        Initializes empty edge sets for the node in both forward and reverse
        adjacency mappings.

        Args:
            node: The identifier for the node to add.
        """
        self._nodes.add(node)
        if node not in self._edges:
            self._edges[node] = set()
        if node not in self._reverse_edges:
            self._reverse_edges[node] = set()

    def add_edge(self, source: str, target: str) -> None:
        """Add a directed edge from source to target.

        Both nodes are automatically added to the graph if they don't exist.
        The edge represents that `source` depends on `target`.

        Args:
            source: The node that depends on target (edge origin).
            target: The node that source depends on (edge destination).
        """
        self.add_node(source)
        self.add_node(target)
        self._edges[source].add(target)
        self._reverse_edges[target].add(source)

    def __contains__(self, node: str) -> bool:
        """Check if a node exists in the graph.

        Args:
            node: The node identifier to check.

        Returns:
            True if the node is in the graph, False otherwise.
        """
        return node in self._nodes

    def __getitem__(self, node: str) -> set[str]:
        """Get the outgoing neighbors (dependencies) of a node.

        Args:
            node: The node to get dependencies for.

        Returns:
            Set of nodes that the given node depends on. Returns empty set
            if the node doesn't exist or has no dependencies.
        """
        return self._edges.get(node, set())

    def nodes(self) -> set[str]:
        """Return all nodes in the graph.

        Returns:
            A set containing all node identifiers in the graph.
        """
        return self._nodes

    def has_edge(self, source: str, target: str) -> bool:
        """Check if a directed edge exists from source to target.

        Args:
            source: The potential edge origin.
            target: The potential edge destination.

        Returns:
            True if an edge exists from source to target, False otherwise.
        """
        return target in self._edges.get(source, set())

    def ancestors(self, target: str) -> set[str]:
        """Find all nodes that can reach the target node (transitive dependents).

        Performs a breadth-first traversal of the reverse edges to find all
        nodes that directly or indirectly depend on the target. This is useful
        for determining the "blast radius" of a change to a package.

        Args:
            target: The node to find ancestors for.

        Returns:
            Set of all nodes that have a path to target (i.e., all packages
            that depend on target, directly or transitively). Does not include
            target itself.
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
        """Find the shortest path length between source and target.

        Uses breadth-first search to find the minimum number of edges
        between two nodes. Useful for determining dependency depth.

        Args:
            source: The starting node.
            target: The destination node.

        Returns:
            The number of edges in the shortest path from source to target.
            Returns 0 if source and target are the same node.

        Raises:
            ValueError: If either node is not in the graph, or if no path
                exists between the nodes.
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
        """Topologically sort a subset of nodes in the graph.

        Performs Kahn's algorithm for topological sorting on the specified
        subset of nodes. The result is ordered such that dependencies come
        before their dependents.

        In the dependency graph, an edge A → B means "A depends on B".
        The topological sort ensures B appears before A in the result.

        This is useful for ordering packages by their dependency relationships,
        ensuring that dependencies are processed before their dependents.

        Args:
            nodes: Set of node identifiers to sort. Only edges between nodes
                in this set are considered.

        Returns:
            List of nodes in topological order (dependencies before dependents).
            If multiple valid orderings exist, the result is deterministic but
            arbitrary among the valid orderings.

        Raises:
            ValueError: If the subgraph contains a cycle, making topological
                sort impossible.

        Example:
            >>> g = DiGraph()
            >>> g.add_edge("pkg2", "pkg1")  # pkg2 depends on pkg1
            >>> g.add_edge("pkg1", "pyrig")  # pkg1 depends on pyrig
            >>> g.topological_sort_subgraph({"pyrig", "pkg1", "pkg2"})
            ['pyrig', 'pkg1', 'pkg2']  # Dependencies first
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
