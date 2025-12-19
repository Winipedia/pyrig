"""module for the following module path (maybe truncated).

tests.test_pyrig.test_modules.test_package
"""

import importlib.metadata
import os
import sys
from contextlib import chdir
from pathlib import Path
from types import ModuleType

import pytest
from pytest_mock import MockFixture

import pyrig
from pyrig import src
from pyrig.dev.utils import packages
from pyrig.dev.utils.packages import find_packages
from pyrig.src.modules.module import (
    import_module_from_file,
    make_obj_importpath,
)
from pyrig.src.modules.package import (
    DependencyGraph,
    create_package,
    get_modules_and_packages_from_package,
    get_objs_from_obj,
    get_pkg_name_from_cwd,
    get_pkg_name_from_project_name,
    get_project_name_from_cwd,
    get_project_name_from_pkg_name,
    get_same_modules_from_deps_depen_on_dep,
    import_pkg_from_dir,
    import_pkg_with_dir_fallback,
    module_is_package,
    walk_package,
)
from pyrig.src.testing.assertions import assert_with_msg


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
        package = import_pkg_from_dir(package_dir)

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
        make_obj_importpath(packages) + "._find_packages",
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
        make_obj_importpath(packages) + "._find_namespace_packages",
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
        assert "setuptools" in deps, "Expected 'setuptools' to be in dependencies"

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

        # Verify topological order: pkg_b should come before pkg_a
        # (because pkg_a depends on pkg_b)
        pkg_b_index = result.index(mock_pkg_b)
        pkg_a_index = result.index(mock_pkg_a)
        assert_with_msg(
            pkg_b_index < pkg_a_index,
            f"Expected pkg_b (index {pkg_b_index}) before pkg_a (index {pkg_a_index}) "
            f"in topological order, got {[m.__name__ for m in result]}",
        )

        # Test with include_self=True
        result = graph.get_all_depending_on(mock_pkg_c, include_self=True)
        assert_with_msg(
            mock_pkg_c in result,
            f"Expected pkg_c in result when include_self=True, got {result}",
        )
        assert_with_msg(
            len(result) == expected_count + 1,
            f"Expected {expected_count + 1} packages with include_self=True, "
            f"got {len(result)}",
        )

        # Verify topological order with include_self:
        # pkg_c should come first, then pkg_b, then pkg_a
        pkg_c_index = result.index(mock_pkg_c)
        pkg_b_index = result.index(mock_pkg_b)
        pkg_a_index = result.index(mock_pkg_a)
        assert_with_msg(
            pkg_c_index < pkg_b_index < pkg_a_index,
            f"Expected topological order: pkg_c, pkg_b, pkg_a. "
            f"Got indices: pkg_c={pkg_c_index}, pkg_b={pkg_b_index}, "
            f"pkg_a={pkg_a_index}",
        )

    def test_import_packages(self) -> None:
        """Test method for import_packages."""
        # Mock importlib.import_module

        # Test importing existing packages
        result = DependencyGraph.import_packages({"sys", "os", "nonexistent"})

        expected_module_count = 2
        assert sys in result, f"Expected sys module in result, got {result}"
        assert os in result, f"Expected os module in result, got {result}"
        assert len(result) == expected_module_count, (
            f"Expected {expected_module_count} modules (sys, os), got {len(result)}"
        )


def test_get_pkg_name_from_project_name() -> None:
    """Test function."""
    project_name = "test-project"
    pkg_name = get_pkg_name_from_project_name(project_name)
    expected_pkg_name = "test_project"
    assert pkg_name == expected_pkg_name, (
        f"Expected {expected_pkg_name}, got {pkg_name}"
    )


def test_get_project_name_from_pkg_name() -> None:
    """Test function."""
    pkg_name = "test_project"
    project_name = get_project_name_from_pkg_name(pkg_name)
    expected_project_name = "test-project"
    assert project_name == expected_project_name, (
        f"Expected {expected_project_name}, got {project_name}"
    )


def test_get_project_name_from_cwd() -> None:
    """Test function."""
    project_name = get_project_name_from_cwd()
    expected_project_name = pyrig.__name__
    assert project_name == expected_project_name, (
        f"Expected {expected_project_name}, got {project_name}"
    )


def test_get_pkg_name_from_cwd() -> None:
    """Test function."""
    pkg_name = get_pkg_name_from_cwd()
    expected_pkg_name = pyrig.__name__
    assert pkg_name == expected_pkg_name, (
        f"Expected {expected_pkg_name}, got {pkg_name}"
    )


def test_get_objs_from_obj(tmp_path: Path) -> None:
    """Test func for get_objs_from_obj."""
    # Create a test module with functions and classes
    module_content = '''"""Test module."""

def func1() -> str:
    """Function 1."""
    return "func1"

def func2() -> str:
    """Function 2."""
    return "func2"

class TestClass1:
    """Test class 1."""

    def method1(self) -> str:
        """Method 1."""
        return "method1"

class TestClass2:
    """Test class 2."""
    pass
'''

    # Create and import the module
    module_file = tmp_path / "test_objs_module.py"
    module_file.write_text(module_content)

    with chdir(tmp_path):
        test_objs_module = import_module_from_file(module_file)

        # Test getting objects from module
        objs = get_objs_from_obj(test_objs_module)

        # Should contain 2 functions and 2 classes
        expected_function_count = 2
        expected_class_count = 2
        expected_total_objects = expected_function_count + expected_class_count
        assert_with_msg(
            len(objs) == expected_total_objects,
            f"Expected {expected_total_objects} objects "
            f"({expected_function_count} functions + {expected_class_count} classes), "
            f"got {len(objs)}",
        )

        # Test getting objects from a class
        class_objs = get_objs_from_obj(test_objs_module.TestClass1)

        # Should contain at least the method1
        method_names = [getattr(obj, "__name__", None) for obj in class_objs]
        assert_with_msg(
            "method1" in method_names,
            f"Expected 'method1' in class methods, got {method_names}",
        )

        # Test with non-module, non-class object
        def test_func() -> None:
            pass

        result = get_objs_from_obj(test_func)
        assert_with_msg(result == [], f"Expected empty list for function, got {result}")


def test_get_same_modules_from_deps_depen_on_dep() -> None:
    """Test function."""
    # Test getting the same module from all packages depending on pyrig

    modules = get_same_modules_from_deps_depen_on_dep(src, pyrig)
    # Should at least include pyrig.src itself
    assert_with_msg(
        len(modules) > 0,
        f"Expected at least one module, got {modules}",
    )
    assert_with_msg(
        src in modules,
        f"Expected pyrig.src in modules, got {modules}",
    )


def test_create_package(tmp_path: Path) -> None:
    """Test function."""
    with chdir(tmp_path):
        package_dir = tmp_path / "test_package"
        assert not package_dir.exists()
        package = create_package(package_dir)
        assert package_dir.exists()
        assert package.__name__ == "test_package"
        assert package_dir.is_dir()
        assert (package_dir / "__init__.py").exists()


def test_import_pkg_with_dir_fallback(tmp_path: Path) -> None:
    """Test function."""
    with chdir(tmp_path):
        non_existing_dir = tmp_path / "non_existing"
        assert not non_existing_dir.exists()
        with pytest.raises(FileNotFoundError):
            import_pkg_with_dir_fallback(non_existing_dir)
        # import nonexisting againto ccheck if somehow cached in sy
        with pytest.raises(FileNotFoundError):
            import_pkg_with_dir_fallback(non_existing_dir)

        existing_dir = tmp_path / "existing"
        existing_dir.mkdir()
        init_file = existing_dir / "__init__.py"
        init_file.write_text('"""Test package."""\n')
        package = import_pkg_with_dir_fallback(existing_dir)
        assert package.__name__ == "existing"


def test_import_pkg_from_dir(tmp_path: Path) -> None:
    """Test function."""
    with chdir(tmp_path):
        non_existing_dir = tmp_path / "non_existing"
        assert not non_existing_dir.exists()
        with pytest.raises(FileNotFoundError):
            import_pkg_from_dir(non_existing_dir)

        package_dir = tmp_path / "test_package"
        package_dir.mkdir()
        init_file = package_dir / "__init__.py"
        init_file.write_text('"""Test package."""\n')
        package = import_pkg_from_dir(package_dir)
        assert package.__name__ == "test_package"

        subdir = package_dir / "subdir"
        subdir.mkdir()
        init_file = subdir / "__init__.py"
        init_file.write_text('"""Test package."""\n')
        package = import_pkg_from_dir(subdir)
        assert package.__name__ == "test_package.subdir"
