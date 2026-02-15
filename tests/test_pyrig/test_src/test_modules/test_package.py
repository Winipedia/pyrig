"""module for the following module path (maybe truncated).

tests.test_pyrig.test_modules.test_package
"""

from contextlib import chdir
from pathlib import Path

import pytest

import pyrig
from pyrig import src
from pyrig.rig import configs
from pyrig.rig.configs.base.base import ConfigFile
from pyrig.src.modules.module import (
    import_module_from_file,
)
from pyrig.src.modules.package import (
    all_deps_depending_on_dep,
    create_package,
    discover_equivalent_modules_across_dependents,
    discover_leaf_subclass_across_dependents,
    discover_subclasses_across_dependents,
    objs_from_obj,
    package_name_from_cwd,
    package_name_from_project_name,
    project_name_from_cwd,
    project_name_from_package_name,
)
from tests.test_pyrig.test_src import test_modules
from tests.test_pyrig.test_src.test_modules.test_class_ import (
    AbstractParent,
    ConcreteChild,
)


def test_package_name_from_project_name() -> None:
    """Test function."""
    project_name = "test-project"
    package_name = package_name_from_project_name(project_name)
    expected_package_name = "test_project"
    assert package_name == expected_package_name, (
        f"Expected {expected_package_name}, got {package_name}"
    )


def test_project_name_from_package_name() -> None:
    """Test function."""
    package_name = "test_project"
    project_name = project_name_from_package_name(package_name)
    expected_project_name = "test-project"
    assert project_name == expected_project_name, (
        f"Expected {expected_project_name}, got {project_name}"
    )


def test_project_name_from_cwd() -> None:
    """Test function."""
    project_name = project_name_from_cwd()
    expected_project_name = pyrig.__name__
    assert project_name == expected_project_name, (
        f"Expected {expected_project_name}, got {project_name}"
    )


def test_package_name_from_cwd() -> None:
    """Test function."""
    package_name = package_name_from_cwd()
    expected_package_name = pyrig.__name__
    assert package_name == expected_package_name, (
        f"Expected {expected_package_name}, got {package_name}"
    )


def test_objs_from_obj(tmp_path: Path) -> None:
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
        objs = objs_from_obj(test_objs_module)

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
        class_objs = objs_from_obj(test_objs_module.TestClass1)

        # Should contain at least the method1
        method_names = [getattr(obj, "__name__", None) for obj in class_objs]
        assert "method1" in method_names, (
            f"Expected 'method1' in class methods, got {method_names}"
        )

        # Test with non-module, non-class object
        def test_func() -> None:
            pass

        result = objs_from_obj(test_func)
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
            cls=ConfigFile, dep=pyrig, load_package_before=configs
        )

    class MyTestConfigFile(ConfigFile):
        pass

    final_leaf = discover_leaf_subclass_across_dependents(
        cls=MyTestConfigFile, dep=pyrig, load_package_before=test_modules
    )
    assert final_leaf is MyTestConfigFile


def test_all_deps_depending_on_dep() -> None:
    """Test function."""
    packages = all_deps_depending_on_dep(pyrig, include_self=True)
    assert pyrig in packages, f"Expected pyrig in packages, got {packages}"
