"""Test module."""

import importlib.metadata

import typer

import pyrig
from pyrig.src.dependency_graph import DependencyGraph


class TestDependencyGraph:
    """Test class."""

    def test_parse_name_and_deps(self) -> None:
        """Test method."""
        name = "pyrig"
        dist = importlib.metadata.distribution(name)
        result_name, result_deps = DependencyGraph.parse_name_and_deps(dist)
        assert result_name == "pyrig", f"Expected 'pyrig', got '{result_name}'"
        assert isinstance(result_deps, list), "Expected deps to be a list"
        assert "typer" in result_deps, "Expected 'typer' to be in dependencies"

    def test_normalize_package_name(self) -> None:
        """Test method."""
        name = "pyrig"
        result = DependencyGraph.normalize_package_name(name)
        expected = "pyrig"
        assert result == expected, f"Expected '{expected}', got '{result}'"

    def test___init__(self) -> None:
        """Test method."""
        # Test it initializes without error
        graph = DependencyGraph()

        # Verify it has nodes (should have installed packages)
        num_nodes = len(graph.nodes())
        assert num_nodes > 0, "Expected graph to have nodes after initialization"

        g1 = DependencyGraph()
        g2 = DependencyGraph()
        assert g1 is g2, (
            "Expected DependencyGraph to be a singleton, got different instances"
        )

    def test_build(self) -> None:
        """Test method."""
        graph = DependencyGraph()

        # Verify that known packages are in the graph
        assert "pyrig" in graph.nodes(), "Expected 'pyrig' to be a node in the graph"
        assert "typer" in graph.nodes(), "Expected 'typer' to be a node in the graph"
        assert "requests" in graph.nodes(), (
            "Expected 'requests' to be a node in the graph"
        )
        assert "nonexistent_package" not in graph.nodes(), (
            "Expected 'nonexistent_package' to not be a node in the graph"
        )

    def test_parse_package_name_from_req(self) -> None:
        """Test method."""
        # Test simple package name
        result = DependencyGraph.parse_package_name_from_req("requests")
        assert result == "requests", f"Expected 'requests', got {result}"

        # Test with version specifier
        result = DependencyGraph.parse_package_name_from_req("requests>=2.0.0")
        assert result == "requests", f"Expected 'requests', got {result}"

        # Test with complex version specifier
        result = DependencyGraph.parse_package_name_from_req("package-name>=1.0,<2.0")
        assert result == "package_name", f"Expected 'package_name', got {result}"

        # Test with extras
        result = DependencyGraph.parse_package_name_from_req("package[extra]>=1.0")
        expected = "package[extra]"
        assert result == expected, f"Expected: {expected}, got {result}"

        # Test with trailing spaces (leading spaces result in empty first split)
        result = DependencyGraph.parse_package_name_from_req("  package-name  >=1.0")
        assert result == "package_name", f"Expected 'package_name', got {result}"

    def test_all_depending_on(self) -> None:
        """Test method."""
        DependencyGraph.clear_cache()  # Clear singleton instance to force rebuild
        dg = DependencyGraph()

        dep_on_typer = dg.all_depending_on("typer", include_self=True)

        assert typer in dep_on_typer, "Expected 'typer' to be in dependents"
        assert pyrig in dep_on_typer, "Expected 'pyrig' to be in dependents"
