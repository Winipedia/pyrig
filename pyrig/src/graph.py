"""A simple directed graph implementation."""


class DiGraph:
    """A simple directed graph implementation."""

    def __init__(self) -> None:
        """Initialize an empty directed graph."""
        self._nodes: set[str] = set()
        self._edges: dict[str, set[str]] = {}  # node -> outgoing neighbors
        self._reverse_edges: dict[str, set[str]] = {}  # node -> incoming neighbors

    def add_node(self, node: str) -> None:
        """Add a node to the graph."""
        self._nodes.add(node)
        if node not in self._edges:
            self._edges[node] = set()
        if node not in self._reverse_edges:
            self._reverse_edges[node] = set()

    def add_edge(self, source: str, target: str) -> None:
        """Add a directed edge from source to target."""
        self.add_node(source)
        self.add_node(target)
        self._edges[source].add(target)
        self._reverse_edges[target].add(source)

    def __contains__(self, node: str) -> bool:
        """Check if a node exists in the graph."""
        return node in self._nodes

    def __getitem__(self, node: str) -> set[str]:
        """Get the outgoing neighbors of a node."""
        return self._edges.get(node, set())

    def nodes(self) -> set[str]:
        """Return all nodes in the graph."""
        return self._nodes

    def has_edge(self, source: str, target: str) -> bool:
        """Check if an edge exists from source to target."""
        return target in self._edges.get(source, set())

    def ancestors(self, target: str) -> set[str]:
        """Find all nodes that can reach the target node.

        Uses BFS to traverse the graph in reverse direction.
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

        Uses BFS to find the shortest path.

        Raises:
            ValueError: If no path exists between source and target.
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
