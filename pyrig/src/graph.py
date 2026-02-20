"""Directed graph implementation for package dependency analysis.

Provides the ``DiGraph`` class, a generic directed graph with bidirectional
traversal optimized for analyzing dependency relationships. ``DiGraph`` is the
base class for ``pyrig.src.dependency_graph.DependencyGraph``, which builds a
graph of installed Python packages to enable pyrig's multi-package discovery
system.

The graph maintains both forward and reverse edges, enabling efficient traversal
in both directions: finding what a node depends on, and finding what depends on
a node (ancestors).
"""

import heapq
from abc import ABC, abstractmethod
from collections import deque


class DiGraph(ABC):
    """Directed graph data structure with bidirectional edge traversal.

    A generic directed graph implementation optimized for dependency analysis.
    Maintains both forward edges (node → targets) and reverse edges (node ← sources)
    for O(1) neighbor lookups in either direction.

    This class provides the foundation for ``DependencyGraph``, which extends it
    to build a graph of installed Python package dependencies. The bidirectional
    design enables efficient queries like "find all packages that depend on X"
    (via ``ancestors``) and "find what X depends on" (via ``__getitem__``).

    Attributes:
        _nodes: Set of all node identifiers in the graph.
        _edges: Forward adjacency mapping (node → set of outgoing neighbors).
        _reverse_edges: Reverse adjacency mapping (node → set of incoming neighbors).
    """

    def __init__(self) -> None:
        """Initialize and build the graph structure."""
        self._nodes: set[str] = set()
        self._edges: dict[str, set[str]] = {}  # node -> outgoing neighbors
        self._reverse_edges: dict[str, set[str]] = {}  # node -> incoming neighbors
        self.build()

    @abstractmethod
    def build(self) -> None:
        """Build the graph structure."""

    def add_node(self, node: str) -> None:
        """Add a node to the graph. Idempotent if node already exists.

        Args:
            node: Node identifier to add.
        """
        self._nodes.add(node)
        if node not in self._edges:
            self._edges[node] = set()
        if node not in self._reverse_edges:
            self._reverse_edges[node] = set()

    def add_edge(self, source: str, target: str) -> None:
        """Add a directed edge from source to target.

        Creates both nodes if they don't exist. In dependency graph context,
        an edge source → target means "source depends on target".

        Args:
            source: Edge origin node.
            target: Edge destination node.
        """
        self.add_node(source)
        self.add_node(target)
        self._edges[source].add(target)
        self._reverse_edges[target].add(source)

    def __contains__(self, node: str) -> bool:
        """Check if a node exists in the graph."""
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
        """Return all node identifiers in the graph."""
        return self._nodes

    def has_edge(self, source: str, target: str) -> bool:
        """Check if a directed edge exists from source to target."""
        return target in self._edges.get(source, set())

    def ancestors(self, target: str) -> set[str]:
        """Find all nodes that have a path to the target node.

        Traverses reverse edges using BFS to find all nodes that can reach
        the target. In dependency graph context (where edge A → B means
        "A depends on B"), this returns all packages that depend on the target,
        either directly or transitively.

        Used by ``DependencyGraph.all_depending_on`` to discover all packages
        in the ecosystem that depend on a given package (e.g., finding all packages
        that depend on pyrig).

        Args:
            target: Node to find ancestors for.

        Returns:
            Set of all nodes with a directed path to target (excludes target itself).
            Returns empty set if target is not in the graph.
        """
        if target not in self:
            return set()

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

    def longest_dependent_chain(self, node: str) -> tuple[str, ...]:
        """Return the longest directed path that "belongs to" (is rooted at) a node.

        "Belongs to" in this context means the path of dependents starting from
        the given node following reverse edges (nodes that depend on the node,
        their dependents, and so on). For example, if `A` is depended-on by
        `B` and `C`, and `D` depends on `C`, then
        `longest_path_belonging_to('A')` -> ``('A', 'C', 'D')``.

        Implementation: depth-first search with memoization (dynamic
        programming). This runs in O(V + E) time on a DAG. Cycle detection is
        performed and a ``ValueError`` is raised if a cycle is encountered.

        Args:
            node: Node identifier to compute longest dependent-path for.

        Returns:
            Tuple of node identifiers representing the longest path starting
            with ``node`` and continuing along dependents.

        Raises:
            ValueError: If the graph contains a cycle,
                making longest path computation impossible.
            ValueError: If the specified node does not exist in the graph.
        """
        if node not in self:
            msg = f"Node '{node}' not found in graph"
            raise ValueError(msg)

        memo: dict[str, tuple[str, ...]] = {}
        visiting: set[str] = set()

        def dfs(n: str) -> tuple[str, ...]:
            if n in memo:
                return memo[n]
            if n in visiting:
                msg = "Cycle detected while computing longest path"
                raise ValueError(msg)

            visiting.add(n)

            # Start with the trivial path (the node itself)
            best: tuple[str, ...] = (n,)

            # Iterate dependents (nodes that have an edge -> n). Sort for
            # deterministic tie-breaking when multiple equal-length paths exist.
            dependents = sorted(self._reverse_edges.get(n, set()))
            for dep in dependents:
                candidate_tail = dfs(dep)
                # candidate_tail begins with dep; prepend current node
                candidate = (n, *candidate_tail)
                # Prefer longer paths; break ties deterministically by tuple
                if len(candidate) > len(best) or (
                    len(candidate) == len(best) and candidate < best
                ):
                    best = candidate

            visiting.remove(n)
            memo[n] = best
            return best

        return dfs(node)

    def topological_sort_subgraph(self, nodes: set[str]) -> list[str]:
        """Sort a subset of nodes in topological order (dependencies first).

        Uses Kahn's algorithm with a min-heap for deterministic ordering when
        multiple nodes have no remaining dependencies. An edge A → B means
        "A depends on B", so B appears before A in the result.

        Used by ``DependencyGraph.all_depending_on`` to ensure packages are
        processed in the correct order: base dependencies before dependents.
        This is critical for discovering plugin implementations where a child
        package's class extends a parent package's class.

        Args:
            nodes: Set of nodes to sort. Only edges between nodes in this set
                are considered; edges to/from nodes outside the set are ignored.

        Returns:
            List of nodes in topological order, with dependencies appearing
            before their dependents.

        Raises:
            ValueError: If the subgraph contains a cycle, making topological
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
            msg = "Cycle detected in subgraph, cannot topologically sort"
            raise ValueError(msg)

        return result
