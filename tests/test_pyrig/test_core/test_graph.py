"""tests module."""

import pytest

from pyrig.core.dependency_graph import DependencyGraph
from pyrig.core.graph import DiGraph


class MyTestDiGraph(DiGraph):
    """Test DiGraph."""

    def build(self) -> None:
        """Simple build method for testing."""


class TestDiGraph:
    """Test class."""

    def test_prune(self) -> None:
        """Test that prune keeps only root and its ancestors."""
        graph = MyTestDiGraph()
        # Build graph:
        #   a -> root -> x -> y
        #   b -> root
        #   c -> x          (c depends on x but not root)
        #   z               (isolated node)
        graph.add_edge("a", "root")
        graph.add_edge("b", "root")
        graph.add_edge("root", "x")
        graph.add_edge("x", "y")
        graph.add_edge("c", "x")
        graph.add_node("z")

        assert len(graph.nodes()) == 7  # noqa: PLR2004

        graph.prune("root")

        # Only root, a, b should remain (ancestors of root + root itself)
        assert graph.nodes() == {"root", "a", "b"}

        # Edges between kept nodes should be preserved
        assert graph.has_edge("a", "root")
        assert graph.has_edge("b", "root")

        # Edges to pruned nodes should be gone
        assert not graph.has_edge("root", "x")

        # Pruned nodes are not in the graph
        assert "x" not in graph
        assert "y" not in graph
        assert "c" not in graph
        assert "z" not in graph

    def test_prune_no_ancestors(self) -> None:
        """Test pruning when root has no ancestors."""
        graph = MyTestDiGraph()
        graph.add_edge("a", "b")
        graph.add_edge("b", "c")
        graph.add_node("root")

        graph.prune("root")

        assert graph.nodes() == {"root"}

    def test_prune_transitive_ancestors(self) -> None:
        """Test that prune keeps transitive ancestors."""
        graph = MyTestDiGraph()
        # d -> c -> b -> a (d transitively depends on a)
        graph.add_edge("d", "c")
        graph.add_edge("c", "b")
        graph.add_edge("b", "a")
        graph.add_node("unrelated")

        graph.prune("a")

        assert graph.nodes() == {"a", "b", "c", "d"}
        assert graph.has_edge("b", "a")
        assert graph.has_edge("c", "b")
        assert graph.has_edge("d", "c")
        assert "unrelated" not in graph

    def test_sorted_ancestors(self) -> None:
        """Test method."""
        graph = DependencyGraph()
        deps = graph.sorted_ancestors("typer")
        assert deps == ["pyrig"]

    def test_longest_dependent_chain(self) -> None:
        """Test method."""
        graph = MyTestDiGraph()

        # Build a more complex acyclic graph using letters.
        # Edges are added as (source, target) meaning "source depends on target".
        # Graph structure (dependents flow left-to-right):
        # A <- B <- H <- I
        # A <- C <- E <- K <- L
        # A <- C <- J
        # A <- D <- F
        # (so the longest dependent chain for A is A -> C -> E -> K -> L)

        graph.add_edge("B", "A")
        graph.add_edge("C", "A")
        graph.add_edge("D", "A")

        graph.add_edge("H", "B")
        graph.add_edge("I", "H")

        graph.add_edge("E", "C")
        graph.add_edge("K", "E")
        graph.add_edge("L", "K")
        graph.add_edge("J", "C")

        graph.add_edge("F", "D")

        # Longest dependent path belonging to A should be A -> C -> E -> K -> L
        assert graph.longest_dependent_chain("A") == ("A", "C", "E", "K", "L")

        # Shorter chains
        assert graph.longest_dependent_chain("B") == ("B", "H", "I")
        assert graph.longest_dependent_chain("D") == ("D", "F")

        # A node with no dependents returns itself
        graph.add_node("Z")
        assert graph.longest_dependent_chain("Z") == ("Z",)

    def test_build(self) -> None:
        """Test method."""
        graph = MyTestDiGraph()
        # assert all empty
        assert len(graph.nodes()) == 0

    def test___init__(self) -> None:
        """Test DiGraph initialization creates empty graph."""
        graph = MyTestDiGraph()
        assert len(graph.nodes()) == 0

    def test_add_node(self) -> None:
        """Test adding nodes to the graph."""
        graph = MyTestDiGraph()
        graph.add_node("a")
        graph.add_node("b")

        assert "a" in graph
        assert "b" in graph
        assert len(graph.nodes()) == 2  # noqa: PLR2004

        # Adding same node twice should not duplicate
        graph.add_node("a")
        assert len(graph.nodes()) == 2  # noqa: PLR2004

    def test_add_edge(self) -> None:
        """Test adding edges to the graph."""
        graph = MyTestDiGraph()
        graph.add_edge("a", "b")

        # Nodes should be created automatically
        assert "a" in graph
        assert "b" in graph

        # Edge should exist
        assert graph.has_edge("a", "b")
        assert not graph.has_edge("b", "a")  # directed graph

    def test___contains__(self) -> None:
        """Test node membership check."""
        graph = MyTestDiGraph()
        graph.add_node("a")

        assert "a" in graph
        assert "b" not in graph

    def test___getitem__(self) -> None:
        """Test getting outgoing neighbors of a node."""
        graph = MyTestDiGraph()
        graph.add_edge("a", "b")
        graph.add_edge("a", "c")
        graph.add_edge("b", "c")

        assert graph["a"] == {"b", "c"}
        assert graph["b"] == {"c"}
        assert graph["c"] == set()  # no outgoing edges
        assert graph["x"] == set()  # non-existent node

    def test_nodes(self) -> None:
        """Test getting all nodes from the graph."""
        graph = MyTestDiGraph()
        graph.add_node("a")
        graph.add_node("b")
        graph.add_edge("c", "d")

        assert graph.nodes() == {"a", "b", "c", "d"}

    def test_has_edge(self) -> None:
        """Test checking if edge exists."""
        graph = MyTestDiGraph()
        graph.add_edge("a", "b")

        assert graph.has_edge("a", "b")
        assert not graph.has_edge("b", "a")
        assert not graph.has_edge("a", "c")
        assert not graph.has_edge("x", "y")

    def test_ancestors(self) -> None:
        """Test finding all ancestors of a node."""
        graph = MyTestDiGraph()
        # Build graph: a -> b -> c -> d
        #              e -> c
        graph.add_edge("a", "b")
        graph.add_edge("b", "c")
        graph.add_edge("c", "d")
        graph.add_edge("e", "c")

        # Ancestors of d: a, b, c, e (all can reach d)
        assert graph.ancestors("d") == {"a", "b", "c", "e"}

        # Ancestors of c: a, b, e
        assert graph.ancestors("c") == {"a", "b", "e"}

        # Ancestors of a: none (it's a root)
        assert graph.ancestors("a") == set()

        # Ancestors of non-existent node
        assert graph.ancestors("x") == set()

    def test_topological_sort_subgraph(self) -> None:
        """Test topological sorting of a subgraph."""
        graph = MyTestDiGraph()
        # Build graph: pyrig <- package1 <- package2
        # (package2 depends on package1, package1 depends on pyrig)
        graph.add_edge("package2", "package1")
        graph.add_edge("package1", "pyrig")

        # Sort should give: pyrig, package1, package2 (dependencies first)
        result = graph.topological_sort_subgraph({"pyrig", "package1", "package2"})
        assert result == ["pyrig", "package1", "package2"]

        # Test with more complex graph
        graph2 = MyTestDiGraph()
        # a <- b <- d
        # a <- c <- d
        # (d depends on both b and c, both depend on a)
        graph2.add_edge("b", "a")
        graph2.add_edge("c", "a")
        graph2.add_edge("d", "b")
        graph2.add_edge("d", "c")

        result2 = graph2.topological_sort_subgraph({"a", "b", "c", "d"})
        # a must come first, d must come last
        assert result2[0] == "a"
        assert result2[-1] == "d"
        # b and c can be in any order, but both before d
        assert result2.index("b") < result2.index("d")
        assert result2.index("c") < result2.index("d")

    def test_topological_sort_subgraph_with_cycle(self) -> None:
        """Test that topological sort raises error on cycles."""
        graph = MyTestDiGraph()
        # Create a cycle: a -> b -> c -> a
        graph.add_edge("a", "b")
        graph.add_edge("b", "c")
        graph.add_edge("c", "a")

        with pytest.raises(ValueError, match="Cycle detected"):
            graph.topological_sort_subgraph({"a", "b", "c"})

    def test_topological_sort_subgraph_empty(self) -> None:
        """Test topological sort with empty set."""
        graph = MyTestDiGraph()
        graph.add_edge("a", "b")

        result = graph.topological_sort_subgraph(set())
        assert result == []

    def test_topological_sort_subgraph_single_node(self) -> None:
        """Test topological sort with single node."""
        graph = MyTestDiGraph()
        graph.add_node("a")

        result = graph.topological_sort_subgraph({"a"})
        assert result == ["a"]
