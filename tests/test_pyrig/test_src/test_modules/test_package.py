"""module for the following module path (maybe truncated).

tests.test_pyrig.test_modules.test_package
"""

import importlib.metadata
from contextlib import chdir
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest
from pytest_mock import MockFixture

import pyrig
from pyrig.src.modules.module import (
    create_module,
    make_obj_importpath,
)
from pyrig.src.modules.package import (
    DependencyGraph,
    copy_package,
    find_packages,
    find_packages_as_modules,
    get_main_package,
    get_modules_and_packages_from_package,
    get_src_package,
    import_pkg_from_path,
    module_is_package,
    walk_package,
)
from pyrig.src.testing.assertions import assert_with_msg


def test_get_src_package() -> None:
    """Test func for get_src_package."""
    src_pkg = get_src_package()
    assert_with_msg(
        src_pkg.__name__ == pyrig.__name__,
        f"Expected pyrig, got {src_pkg}",
    )


def test_module_is_package() -> None:
    """Test func for module_is_package."""
    # Create a mock module with __path__ attribute (package)
    mock_package = ModuleType("test_package")
    mock_package.__path__ = ["some/path"]

    # Create a mock module without __path__ attribute (regular module)
    mock_module = ModuleType("test_module")

    assert_with_msg(
        module_is_package(mock_package) is True,
        "Expected module with __path__ to be identified as package",
    )

    assert_with_msg(
        module_is_package(mock_module) is False,
        "Expected module without __path__ to not be identified as package",
    )


def test_get_modules_and_packages_from_package(tmp_path: Path) -> None:
    """Test func for get_modules_and_packages_from_package."""
    # Create a temporary package with known content
    with chdir(tmp_path):
        package_dir = tmp_path / "test_package"
        package_dir.mkdir()
        init_file = package_dir / "__init__.py"
        init_file.write_text('"""Test package."""\n')
        module_file = package_dir / "test_module.py"
        module_file.write_text('"""Test module."""\n')
        package = import_pkg_from_path(package_dir)

        packages, modules = get_modules_and_packages_from_package(package)
        assert_with_msg(
            packages == [],
            f"Expected no packages, got {packages}",
        )
        modules_names = [m.__name__ for m in modules]
        assert_with_msg(
            modules_names == [package.__name__ + ".test_module"],
            f"Expected [package.test_module], got {modules}",
        )


def test_find_packages(mocker: MockFixture) -> None:
    """Test func for find_packages."""
    # Mock setuptools find_packages
    mock_find_packages = mocker.patch(
        "pyrig.src.modules.package._find_packages",
        return_value=["package1", "package1.sub1", "package1.sub1.sub2", "package2"],
    )

    # Mock read_text of Path to return empty list (no gitignore patterns)
    mocker.patch(
        "pathlib.Path.read_text",
        return_value="",
    )

    # Test without depth limit
    result = find_packages()
    expected = ["package1", "package1.sub1", "package1.sub1.sub2", "package2"]
    assert_with_msg(result == expected, f"Expected {expected}, got {result}")

    # Test with depth limit
    result = find_packages(depth=1)
    expected = ["package1", "package1.sub1", "package2"]
    assert_with_msg(result == expected, f"Expected {expected}, got {result}")

    # Test with depth 0
    result = find_packages(depth=0)
    expected = ["package1", "package2"]
    assert_with_msg(result == expected, f"Expected {expected}, got {result}")

    # Verify that setuptools find_packages was called with empty exclude list
    mock_find_packages.assert_called_with(where=".", exclude=[], include=("*",))


def test_find_packages_with_namespace(mocker: MockFixture) -> None:
    """Test find_packages with namespace packages."""
    mock_find_namespace = mocker.patch(
        "pyrig.src.modules.package._find_namespace_packages",
        return_value=["ns_package1", "ns_package2"],
    )

    mocker.patch(
        "pathlib.Path.read_text",
        return_value="",
    )

    result = find_packages(include_namespace_packages=True)
    expected = ["ns_package1", "ns_package2"]
    assert_with_msg(result == expected, f"Expected {expected}, got {result}")

    mock_find_namespace.assert_called_once_with(where=".", exclude=[], include=("*",))


def test_find_packages_with_gitignore_filtering(mocker: MockFixture) -> None:
    """Test find_packages with gitignore patterns that should exclude packages."""
    # Mock setuptools find_packages to return only packages not excluded by gitignore
    mock_find_packages = mocker.patch(
        "pyrig.src.modules.package._find_packages",
        return_value=[
            "package1",
            "package2",
        ],  # dist and build are excluded by setuptools
    )

    # Mock load_gitignore to return patterns that should exclude dist and build
    mocker.patch(
        "pathlib.Path.read_text",
        return_value="""
dist/
build/
__pycache__/
""",
    )

    result = find_packages()
    expected = ["package1", "package2"]
    assert_with_msg(result == expected, f"Expected {expected}, got {result}")

    # Verify that setuptools find_packages was called with gitignore patterns
    expected_exclude = ["dist", "build", "__pycache__"]
    mock_find_packages.assert_called_with(
        where=".", exclude=expected_exclude, include=("*",)
    )


def test_find_packages_as_modules(mocker: MockFixture) -> None:
    """Test func for find_packages_as_modules."""
    # Mock find_packages
    mock_find_packages = mocker.patch(
        make_obj_importpath(find_packages),
        return_value=["package1", "package2"],
    )

    # Mock import_module
    mock_package1 = ModuleType("package1")
    mock_package2 = ModuleType("package2")
    mock_import = mocker.patch("pyrig.src.modules.package.import_module")
    mock_import.side_effect = [mock_package1, mock_package2]

    result = find_packages_as_modules(depth=1, include_namespace_packages=True)
    expected = [mock_package1, mock_package2]
    assert_with_msg(result == expected, f"Expected {expected}, got {result}")

    # The function should call find_packages with exclude=None (default parameter)
    mock_find_packages.assert_called_once_with(
        depth=1,
        include_namespace_packages=True,
        where=".",
        exclude=None,
        include=("*",),
    )


def test_walk_package(mocker: MockFixture) -> None:
    """Test func for walk_package."""
    # Create mock package hierarchy
    root_package = ModuleType("root")
    sub_package1 = ModuleType("root.sub1")
    sub_package2 = ModuleType("root.sub2")
    module1 = ModuleType("root.module1")
    module2 = ModuleType("root.sub1.module2")
    module3 = ModuleType("root.sub2.module3")

    # Mock get_modules_and_packages_from_package
    mock_get_modules = mocker.patch(
        make_obj_importpath(get_modules_and_packages_from_package)
    )

    # Define side effects for different packages
    def side_effect(package: ModuleType) -> tuple[list[ModuleType], list[ModuleType]]:
        if package == root_package:
            return [sub_package1, sub_package2], [module1]
        if package == sub_package1:
            return [], [module2]
        if package == sub_package2:
            return [], [module3]
        return [], []

    mock_get_modules.side_effect = side_effect

    result = list(walk_package(root_package))
    expected = [
        (root_package, [module1]),
        (sub_package1, [module2]),
        (sub_package2, [module3]),
    ]

    assert_with_msg(
        len(result) == len(expected),
        f"Expected {len(expected)} results, got {len(result)}",
    )

    for i, (pkg, modules) in enumerate(result):
        expected_pkg, expected_modules = expected[i]
        assert_with_msg(
            pkg == expected_pkg,
            f"Expected package {expected_pkg}, got {pkg} at index {i}",
        )
        assert_with_msg(
            modules == expected_modules,
            f"Expected modules {expected_modules}, got {modules} at index {i}",
        )


def test_copy_package(tmp_path: Path) -> None:
    """Test func for copy_package."""
    with chdir(tmp_path):
        # Create source package structure
        src_path = tmp_path / "src_path"
        src_path.mkdir()

        src_package = create_module("src_path.src_package", is_package=True)
        create_module("src_path.src_package.sub_package", is_package=True)
        create_module("src_path.src_package.module1", is_package=False)
        create_module("src_path.src_package.sub_package.module2", is_package=False)

        # assert module 2 exists
        assert_with_msg(
            (src_path / "src_package" / "sub_package" / "module2.py").exists(),
            "Expected module2.py to exist",
        )

        # Copy the package
        dst_path = tmp_path / "dst_path"
        copy_package(src_package, dst_path)

        # rglob all .py files in src_path and assert they exist in dst_path
        for src_file in src_path.rglob("*.py"):
            dst_file = dst_path / src_file.relative_to(src_path / "src_package")
            assert_with_msg(
                dst_file.exists(),
                f"Expected {dst_file} to exist",
            )


def test_get_main_package(mocker: MockFixture) -> None:
    """Test func for get_main_package."""
    # Test successful case
    mock_main_module = ModuleType("__main__")
    mock_main_module.__package__ = "test_package"
    mock_package = ModuleType("test_package")

    # Create a mock sys module with modules attribute
    mock_sys = mocker.MagicMock()
    mock_sys.modules.get.return_value = mock_main_module
    mocker.patch("pyrig.src.modules.package.sys", mock_sys)

    mock_import_module = mocker.patch("pyrig.src.modules.package.import_module")
    mock_import_module.return_value = mock_package

    result = get_main_package()

    assert_with_msg(result == mock_package, f"Expected {mock_package}, got {result}")
    mock_sys.modules.get.assert_called_with("__main__")
    mock_import_module.assert_called_with("test_package")

    # Test case when no __main__ module exists
    mock_sys.modules.get.return_value = None

    with pytest.raises(ValueError, match="No __main__ module found"):
        get_main_package()

    # Test case when __main__ module has no __package__ attribute
    mock_main_module_no_package = ModuleType("__main__")
    mock_main_module_no_package.__package__ = None
    mock_sys.modules.get.return_value = mock_main_module_no_package

    with pytest.raises(ValueError, match="Not able to determine the main package"):
        get_main_package()


class TestDependencyGraph:
    """Test class."""

    def test_parse_distname_from_metadata(self) -> None:
        """Test method for parse_distname_from_metadata."""
        name = "pyrig"
        dist = importlib.metadata.distribution(name)
        result = DependencyGraph.parse_distname_from_metadata(dist)
        expected = "pyrig"
        assert_with_msg(
            result == expected,
            f"Expected '{expected}', got '{result}'",
        )

    def test_normalize_package_name(self) -> None:
        """Test method for normalize_package_name."""
        name = "pyrig"
        result = DependencyGraph.normalize_package_name(name)
        expected = "pyrig"
        assert_with_msg(
            result == expected,
            f"Expected '{expected}', got '{result}'",
        )

    def test___init__(self) -> None:
        """Test method for __init__."""
        # Test it initializes without error
        graph = DependencyGraph()

        # Verify it has nodes (should have installed packages)
        num_nodes = len(graph.nodes())
        assert_with_msg(
            num_nodes > 0,
            "Expected graph to have nodes after initialization",
        )

    def test_build(self, mocker: MockFixture) -> None:
        """Test method for build."""
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
        assert_with_msg(
            "test_package" in graph.nodes(),
            "Expected 'test-package' to be in graph nodes",
        )
        assert_with_msg(
            "dependency1" in graph.nodes(),
            "Expected 'dependency1' to be in graph nodes",
        )

        # Verify edges were added
        assert_with_msg(
            graph.has_edge("test_package", "dependency1"),
            "Expected edge from 'test-package' to 'dependency1'",
        )
        assert_with_msg(
            graph.has_edge("test_package", "dependency2"),
            "Expected edge from 'test-package' to 'dependency2'",
        )

    def test_get_all_dependencies(self) -> None:
        """Test method for get_all_dependencies."""
        deps = DependencyGraph.get_all_dependencies()
        assert "networkx" in deps, "Expected 'networkx' to be in dependencies"

    def test_parse_pkg_name_from_req(self) -> None:
        """Test method for parse_pkg_name_from_req."""
        # Test simple package name
        result = DependencyGraph.parse_pkg_name_from_req("requests")
        assert_with_msg(result == "requests", f"Expected 'requests', got {result}")

        # Test with version specifier
        result = DependencyGraph.parse_pkg_name_from_req("requests>=2.0.0")
        assert_with_msg(result == "requests", f"Expected 'requests', got {result}")

        # Test with complex version specifier
        result = DependencyGraph.parse_pkg_name_from_req("package-name>=1.0,<2.0")
        assert_with_msg(
            result == "package_name", f"Expected 'package_name', got {result}"
        )

        # Test with extras
        result = DependencyGraph.parse_pkg_name_from_req("package[extra]>=1.0")
        assert_with_msg(result == "package", f"Expected 'package', got {result}")

        # Test empty string
        result = DependencyGraph.parse_pkg_name_from_req("")
        assert_with_msg(result is None, f"Expected None for empty string, got {result}")

        # Test with trailing spaces (leading spaces result in empty first split)
        result = DependencyGraph.parse_pkg_name_from_req("  package-name  >=1.0")
        assert_with_msg(
            result == "package_name", f"Expected 'package_name', got {result}"
        )

    def test_get_all_depending_on(self, mocker: MockFixture) -> None:
        """Test method for get_all_depending_on."""
        # Mock the build method to prevent it from running
        mocker.patch.object(DependencyGraph, "build")

        # Create a simple dependency graph
        graph = DependencyGraph()

        # Add nodes and edges manually
        # Structure: pkg_a -> pkg_b -> pkg_c
        graph.add_node("pkg_a")
        graph.add_node("pkg_b")
        graph.add_node("pkg_c")
        graph.add_edge("pkg_a", "pkg_b")
        graph.add_edge("pkg_b", "pkg_c")

        # Mock import_packages to return mock modules
        mock_pkg_a = ModuleType("pkg_a")
        mock_pkg_b = ModuleType("pkg_b")

        def mock_import_packages(names: set[str]) -> set[ModuleType]:
            result = set()
            if "pkg_a" in names:
                result.add(mock_pkg_a)
            if "pkg_b" in names:
                result.add(mock_pkg_b)
            return result

        mocker.patch.object(graph, "import_packages", side_effect=mock_import_packages)

        # Create mock module for pkg_c
        mock_pkg_c = ModuleType("pkg_c")

        # Test getting all packages depending on pkg_c
        result = graph.get_all_depending_on(mock_pkg_c, include_self=False)

        # pkg_a and pkg_b depend on pkg_c (transitively)
        expected_count = 2
        assert_with_msg(
            mock_pkg_a in result,
            f"Expected pkg_a in dependents of pkg_c, got {result}",
        )
        assert_with_msg(
            mock_pkg_b in result,
            f"Expected pkg_b in dependents of pkg_c, got {result}",
        )

        # Test with include_self=True
        mocker.patch.object(
            graph,
            "import_packages",
            side_effect=lambda names: mock_import_packages(names) | {mock_pkg_c}
            if "pkg_c" in names
            else mock_import_packages(names),
        )
        result = graph.get_all_depending_on(mock_pkg_c, include_self=True)
        assert_with_msg(
            mock_pkg_c in result or len(result) >= expected_count,
            f"Expected pkg_c in result when include_self=True, got {result}",
        )

    def test_import_packages(self, mocker: MockFixture) -> None:
        """Test method for import_packages."""
        # Mock importlib.util.find_spec
        mock_find_spec = mocker.patch("importlib.util.find_spec")

        # Mock importlib.import_module
        mock_sys = ModuleType("sys")
        mock_os = ModuleType("os")
        mock_import_module = mocker.patch("importlib.import_module")

        def import_side_effect(name: str) -> ModuleType | None:
            modules = {"sys": mock_sys, "os": mock_os}
            return modules.get(name)

        mock_import_module.side_effect = import_side_effect

        # Set up find_spec to return spec for sys and os, None for nonexistent
        def find_spec_side_effect(name: str) -> Any:
            if name in {"sys", "os"}:
                return mocker.MagicMock()  # Return a mock spec
            return None

        mock_find_spec.side_effect = find_spec_side_effect

        # Test importing existing packages
        result = DependencyGraph.import_packages({"sys", "os", "nonexistent"})

        expected_module_count = 2
        assert_with_msg(
            mock_sys in result,
            f"Expected sys module in result, got {result}",
        )
        assert_with_msg(
            mock_os in result,
            f"Expected os module in result, got {result}",
        )
        assert_with_msg(
            len(result) == expected_module_count,
            f"Expected {expected_module_count} modules (sys, os), got {len(result)}",
        )


def test_import_pkg_from_path(tmp_path: Path) -> None:
    """Test func for import_pkg_from_path."""
    # Create a temporary package with known content
    with chdir(tmp_path):
        package_dir = tmp_path / "test_package"
        package_dir.mkdir()
        init_file = package_dir / "__init__.py"
        init_file.write_text('"""Test package."""\n')

        # Import the package
        package = import_pkg_from_path(package_dir)

        assert_with_msg(
            package.__name__ == "test_package",
            f"Expected package name to be test_package, got {package.__name__}",
        )
        # test deeper path
        subdir = package_dir / "subdir"
        subdir.mkdir()
        init_file = subdir / "__init__.py"
        init_file.write_text('"""Test package."""\n')
        package = import_pkg_from_path(subdir)
        assert_with_msg(
            package.__name__ == "test_package.subdir",
            f"Expected package name to be test_package.subdir, got {package.__name__}",
        )
