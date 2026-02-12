"""module for the following module path (maybe truncated).

tests.test_pyrig.test_modules.test_package
"""

from contextlib import chdir
from pathlib import Path

import pytest
from pytest_mock import MockFixture

import pyrig
from pyrig import src
from pyrig.rig import configs
from pyrig.rig.configs.base.base import ConfigFile
from pyrig.rig.utils import packages
from pyrig.rig.utils.packages import find_packages
from pyrig.src.modules.module import (
    import_module_from_file,
    make_obj_importpath,
)
from pyrig.src.modules.package import (
    create_package,
    discover_equivalent_modules_across_dependents,
    discover_leaf_subclass_across_dependents,
    discover_subclasses_across_dependents,
    get_all_deps_depending_on_dep,
    get_objs_from_obj,
    get_pkg_name_from_cwd,
    get_pkg_name_from_project_name,
    get_project_name_from_cwd,
    get_project_name_from_pkg_name,
)
from tests.test_pyrig.test_src import test_modules
from tests.test_pyrig.test_src.test_modules.test_class_ import (
    AbstractParent,
    ConcreteChild,
)


def test_find_packages(mocker: MockFixture) -> None:
    """Test function."""
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
    assert result == expected, f"Expected {expected}, got {result}"

    # Test with depth limit
    result = find_packages(depth=1)
    expected = ["package1", "package1.sub1", "package2"]
    assert result == expected, f"Expected {expected}, got {result}"

    # Test with depth 0
    result = find_packages(depth=0)
    expected = ["package1", "package2"]
    assert result == expected, f"Expected {expected}, got {result}"

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
    assert result == expected, f"Expected {expected}, got {result}"

    mock_find_namespace.assert_called_once_with(where=".", exclude=[], include=("*",))


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
    """Test function."""
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
        assert len(objs) == expected_total_objects, (
            f"Expected {expected_total_objects} objects "
            f"({expected_function_count} functions + {expected_class_count} classes), "
            f"got {len(objs)}"
        )

        # Test getting objects from a class
        class_objs = get_objs_from_obj(test_objs_module.TestClass1)

        # Should contain at least the method1
        method_names = [getattr(obj, "__name__", None) for obj in class_objs]
        assert "method1" in method_names, (
            f"Expected 'method1' in class methods, got {method_names}"
        )

        # Test with non-module, non-class object
        def test_func() -> None:
            pass

        result = get_objs_from_obj(test_func)
        assert result == [], f"Expected empty list for function, got {result}"


def test_discover_equivalent_modules_across_dependents() -> None:
    """Test function."""
    # Test getting the same module from all packages depending on pyrig

    modules = discover_equivalent_modules_across_dependents(src, pyrig)
    # Should at least include pyrig.src itself
    assert len(modules) > 0, f"Expected at least one module, got {modules}"
    assert src in modules, f"Expected pyrig.src in modules, got {modules}"


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


def test_discover_subclasses_across_dependents() -> None:
    """Test func."""
    subclasses = discover_subclasses_across_dependents(
        AbstractParent, pyrig, test_modules, exclude_abstract=True
    )
    assert ConcreteChild in subclasses, (
        f"Expected ConcreteChild in non-abstract subclasses, got {subclasses}"
    )


def test_discover_leaf_subclass_across_dependents() -> None:
    """Test function."""
    with pytest.raises(ValueError, match="Multiple final leaves found"):
        discover_leaf_subclass_across_dependents(
            cls=ConfigFile, dep=pyrig, load_pkg_before=configs
        )

    class MyTestConfigFile(ConfigFile):
        pass

    final_leaf = discover_leaf_subclass_across_dependents(
        cls=MyTestConfigFile, dep=pyrig, load_pkg_before=test_modules
    )
    assert final_leaf is MyTestConfigFile


def test_get_all_deps_depending_on_dep() -> None:
    """Test function."""
    pkgs = get_all_deps_depending_on_dep(pyrig, include_self=True)
    assert pyrig in pkgs, f"Expected pyrig in pkgs, got {pkgs}"
