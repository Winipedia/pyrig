"""Test module."""

import importlib.metadata

from pyrig.core.dependency_graph import DependencyGraph

DEP_GRAPH = DependencyGraph()


class TestDependencyGraph:
    """Test class."""

    def test_parse_name_and_deps(self) -> None:
        """Test method."""
        name = "pyrig"
        dist = importlib.metadata.distribution(name)
        result_name, result_deps = DEP_GRAPH.parse_name_and_deps(dist)
        assert result_name == "pyrig"
        assert "typer" in result_deps

    def test___init__(self) -> None:
        """Test method."""
        # Test it initializes without error

        # Verify it has nodes (should have installed packages)
        num_nodes = len(DEP_GRAPH.nodes())
        assert num_nodes > 0, "Expected graph to have nodes after initialization"

    def test_build(self) -> None:
        """Test method."""
        # Verify that known packages are in the graph
        assert "pyrig" in DEP_GRAPH.nodes()
        assert "typer" in DEP_GRAPH.nodes()
        assert "requests" in DEP_GRAPH.nodes()
        assert "nonexistent_package" not in DEP_GRAPH.nodes()
