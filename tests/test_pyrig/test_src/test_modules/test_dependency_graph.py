"""Test module."""

import importlib.metadata
import os
import sys
from types import ModuleType

from pytest_mock import MockFixture

from pyrig.src.modules.dependency_graph import DependencyGraph


class TestDependencyGraph:
    """Test class."""

    def test_parse_distname_from_metadata(self) -> None:
        """Test method."""
        name = "pyrig"
        dist = importlib.metadata.distribution(name)
        result = DependencyGraph.parse_distname_from_metadata(dist)
        expected = "pyrig"
        assert result == expected, f"Expected '{expected}', got '{result}'"

    def test_normalize_package_name(self) -> None:
        """Test method."""
        name = "pyrig"
        result = DependencyGraph.normalize_package_name(name)
        expected = "pyrig"
        assert result == expected, f"Expected '{expected}', got '{result}'"

    def test___init__(self) -> None:
        """Test method."""
        # Test it initializes without error
        graph = DependencyGraph.cached()

        # Verify it has nodes (should have installed packages)
        num_nodes = len(graph.nodes())
        assert num_nodes > 0, "Expected graph to have nodes after initialization"

    def test_build(self, mocker: MockFixture) -> None:
        """Test method."""
        # Create a mock distribution
        mock_dist1 = mocker.MagicMock()
        mock_dist1.metadata = {"Name": "test-package"}
        mock_dist1.requires = ["dependency1>=1.0.0", "dependency2"]

        mock_dist2 = mocker.MagicMock()
        mock_dist2.metadata = {"Name": "dependency1"}
        mock_dist2.requires = None

        # Mock importlib.metadata.distributions
        mocker.patch(
            "importlib.metadata.distributions",
            return_value=[mock_dist1, mock_dist2],
        )

        graph = DependencyGraph()

        # Verify nodes were added
        assert "test_package" in graph.nodes(), (
            "Expected 'test-package' to be in graph nodes"
        )
        assert "dependency1" in graph.nodes(), (
            "Expected 'dependency1' to be in graph nodes"
        )

        # Verify edges were added
        assert graph.has_edge("test_package", "dependency1"), (
            "Expected edge from 'test-package' to 'dependency1'"
        )
        assert graph.has_edge("test_package", "dependency2"), (
            "Expected edge from 'test-package' to 'dependency2'"
        )

    def test_all_dependencies(self) -> None:
        """Test method."""
        deps = DependencyGraph.all_dependencies()
        assert "setuptools" in deps, "Expected 'setuptools' to be in dependencies"

    def test_parse_pkg_name_from_req(self) -> None:
        """Test method."""
        # Test simple package name
        result = DependencyGraph.parse_pkg_name_from_req("requests")
        assert result == "requests", f"Expected 'requests', got {result}"

        # Test with version specifier
        result = DependencyGraph.parse_pkg_name_from_req("requests>=2.0.0")
        assert result == "requests", f"Expected 'requests', got {result}"

        # Test with complex version specifier
        result = DependencyGraph.parse_pkg_name_from_req("package-name>=1.0,<2.0")
        assert result == "package_name", f"Expected 'package_name', got {result}"

        # Test with extras
        result = DependencyGraph.parse_pkg_name_from_req("package[extra]>=1.0")
        expected = "package[extra]"
        assert result == expected, f"Expected: {expected}, got {result}"

        # Test empty string
        result = DependencyGraph.parse_pkg_name_from_req("")
        assert result is None, f"Expected None for empty string, got {result}"

        # Test with trailing spaces (leading spaces result in empty first split)
        result = DependencyGraph.parse_pkg_name_from_req("  package-name  >=1.0")
        assert result == "package_name", f"Expected 'package_name', got {result}"

    def test_all_depending_on(self, mocker: MockFixture) -> None:
        """Test method."""
        # Mock the build method to prevent it from running
        mocker.patch.object(DependencyGraph, "build")

        # Create a simple dependency graph
        graph = DependencyGraph.cached()

        # Add nodes and edges manually
        # Structure: pkg_a -> pkg_b -> pkg_c
        # (pkg_a depends on pkg_b, pkg_b depends on pkg_c)
        graph.add_node("pkg_a")
        graph.add_node("pkg_b")
        graph.add_node("pkg_c")
        graph.add_edge("pkg_a", "pkg_b")
        graph.add_edge("pkg_b", "pkg_c")

        # Mock import_packages to return mock modules in the order they're given
        mock_pkg_a = ModuleType("pkg_a")
        mock_pkg_b = ModuleType("pkg_b")
        mock_pkg_c = ModuleType("pkg_c")

        def mock_import_packages(names: list[str]) -> list[ModuleType]:
            result: list[ModuleType] = []
            for name in names:
                if name == "pkg_a":
                    result.append(mock_pkg_a)
                elif name == "pkg_b":
                    result.append(mock_pkg_b)
                elif name == "pkg_c":
                    result.append(mock_pkg_c)
            return result

        mocker.patch.object(graph, "import_packages", side_effect=mock_import_packages)

        # Test getting all packages depending on pkg_c
        result = graph.all_depending_on(mock_pkg_c, include_self=False)

        # pkg_a and pkg_b depend on pkg_c (transitively)
        expected_count = 2
        assert mock_pkg_a in result, (
            f"Expected pkg_a in dependents of pkg_c, got {result}"
        )
        assert mock_pkg_b in result, (
            f"Expected pkg_b in dependents of pkg_c, got {result}"
        )

        # Verify topological order: pkg_b should come before pkg_a
        # (because pkg_a depends on pkg_b)
        pkg_b_index = result.index(mock_pkg_b)
        pkg_a_index = result.index(mock_pkg_a)
        assert pkg_b_index < pkg_a_index, (
            f"Expected pkg_b (index {pkg_b_index}) before pkg_a (index {pkg_a_index}) "
            f"in topological order, got {[m.__name__ for m in result]}"
        )

        # Test with include_self=True
        result = graph.all_depending_on(mock_pkg_c, include_self=True)
        assert mock_pkg_c in result, (
            f"Expected pkg_c in result when include_self=True, got {result}"
        )
        assert len(result) == expected_count + 1, (
            f"Expected {expected_count + 1} packages with include_self=True, "
            f"got {len(result)}"
        )

        # Verify topological order with include_self:
        # pkg_c should come first, then pkg_b, then pkg_a
        pkg_c_index = result.index(mock_pkg_c)
        pkg_b_index = result.index(mock_pkg_b)
        pkg_a_index = result.index(mock_pkg_a)
        assert pkg_c_index < pkg_b_index < pkg_a_index, (
            f"Expected topological order: pkg_c, pkg_b, pkg_a. "
            f"Got indices: pkg_c={pkg_c_index}, pkg_b={pkg_b_index}, "
            f"pkg_a={pkg_a_index}"
        )

    def test_import_packages(self) -> None:
        """Test method."""
        # Mock importlib.import_module

        # Test importing existing packages
        result = DependencyGraph.import_packages({"sys", "os", "nonexistent"})

        expected_module_count = 2
        assert sys in result, f"Expected sys module in result, got {result}"
        assert os in result, f"Expected os module in result, got {result}"
        assert len(result) == expected_module_count, (
            f"Expected {expected_module_count} modules (sys, os), got {len(result)}"
        )
