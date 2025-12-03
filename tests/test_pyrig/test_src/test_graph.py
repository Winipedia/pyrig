"""tests module."""

import pytest

from pyrig.src.graph import DiGraph


class TestDiGraph:
    """Test class for DiGraph."""

    def test___init__(self) -> None:
        """Test DiGraph initialization creates empty graph."""
        graph = DiGraph()
        assert len(graph.nodes()) == 0

    def test_add_node(self) -> None:
        """Test adding nodes to the graph."""
        graph = DiGraph()
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
        graph = DiGraph()
        graph.add_edge("a", "b")

        # Nodes should be created automatically
        assert "a" in graph
        assert "b" in graph

        # Edge should exist
        assert graph.has_edge("a", "b")
        assert not graph.has_edge("b", "a")  # directed graph

    def test___contains__(self) -> None:
        """Test node membership check."""
        graph = DiGraph()
        graph.add_node("a")

        assert "a" in graph
        assert "b" not in graph

    def test___getitem__(self) -> None:
        """Test getting outgoing neighbors of a node."""
        graph = DiGraph()
        graph.add_edge("a", "b")
        graph.add_edge("a", "c")
        graph.add_edge("b", "c")

        assert graph["a"] == {"b", "c"}
        assert graph["b"] == {"c"}
        assert graph["c"] == set()  # no outgoing edges
        assert graph["x"] == set()  # non-existent node

    def test_nodes(self) -> None:
        """Test getting all nodes from the graph."""
        graph = DiGraph()
        graph.add_node("a")
        graph.add_node("b")
        graph.add_edge("c", "d")

        assert graph.nodes() == {"a", "b", "c", "d"}

    def test_has_edge(self) -> None:
        """Test checking if edge exists."""
        graph = DiGraph()
        graph.add_edge("a", "b")

        assert graph.has_edge("a", "b")
        assert not graph.has_edge("b", "a")
        assert not graph.has_edge("a", "c")
        assert not graph.has_edge("x", "y")

    def test_ancestors(self) -> None:
        """Test finding all ancestors of a node."""
        graph = DiGraph()
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

    def test_shortest_path_length(self) -> None:
        """Test finding shortest path length between nodes."""
        graph = DiGraph()
        # Build graph: a -> b -> c -> d
        #              a -> c (shortcut)
        graph.add_edge("a", "b")
        graph.add_edge("b", "c")
        graph.add_edge("c", "d")
        graph.add_edge("a", "c")

        # Same node
        assert graph.shortest_path_length("a", "a") == 0

        # Direct edge
        assert graph.shortest_path_length("a", "b") == 1

        # Shortest path a -> c is 1 (direct), not 2 (via b)
        assert graph.shortest_path_length("a", "c") == 1

        # Path a -> d: a -> c -> d = 2
        assert graph.shortest_path_length("a", "d") == 2  # noqa: PLR2004

        # No path from d to a (directed graph)
        with pytest.raises(ValueError, match="No path from d to a"):
            graph.shortest_path_length("d", "a")

        # Non-existent node
        with pytest.raises(ValueError, match="Node not in graph"):
            graph.shortest_path_length("a", "x")
