"""module for the following module path (maybe truncated).

tests.test_pyrig.test_modules.test_module
"""

import os
import sys
from contextlib import chdir
from importlib import import_module
from pathlib import Path
from types import ModuleType

import pytest
from pytest_mock import MockFixture

import pyrig
from pyrig import src
from pyrig.src.modules.module import (
    create_module,
    execute_all_functions_from_module,
    get_default_init_module_content,
    get_default_module_content,
    get_executing_module,
    get_isolated_obj_name,
    get_module_content_as_str,
    get_module_of_obj,
    get_objs_from_obj,
    get_same_modules_from_deps_depen_on_dep,
    import_module_from_file,
    import_module_from_path,
    import_module_from_path_with_default,
    import_module_with_default,
    import_obj_from_importpath,
    make_dir_with_init_file,
    make_init_module,
    make_init_modules_for_package,
    make_obj_importpath,
    make_pkg_dir,
    to_module_name,
    to_path,
)
from pyrig.src.testing.assertions import assert_with_msg


def test_get_module_content_as_str(tmp_path: Path) -> None:
    """Test func for get_module_content_as_str."""
    # Create a temporary module file with known content
    module_content = '''"""Test module."""

def test_function() -> str:
    """Test function."""
    return "test"

class TestClass:
    """Test class."""
    pass
'''

    # Create module file
    module_file = tmp_path / "test_module.py"
    module_file.write_text(module_content)

    # Change to tmp_path directory and add to sys.path temporarily
    original_cwd = Path.cwd()
    original_path = sys.path[:]
    os.chdir(tmp_path)
    sys.path.insert(0, str(tmp_path))

    try:
        # Import the module using importlib
        test_module = import_module("test_module")

        # Test getting module content
        result = get_module_content_as_str(test_module)
        assert_with_msg(
            result == module_content,
            f"Expected module content to match, got {result!r}",
        )

    finally:
        # Clean up
        os.chdir(original_cwd)
        sys.path[:] = original_path
        if "test_module" in sys.modules:
            del sys.modules["test_module"]


def test_to_module_name() -> None:
    """Test func for to_module_name."""
    # Test with Path objects
    path_result = to_module_name(Path("src/package/module.py"))
    assert_with_msg(
        path_result == "src.package.module",
        f"Expected 'src.package.module', got {path_result!r}",
    )

    subpackage_result = to_module_name(Path("package/subpackage"))
    assert_with_msg(
        subpackage_result == "package.subpackage",
        f"Expected 'package.subpackage', got {subpackage_result!r}",
    )

    # Test with string paths
    str_result = to_module_name("src/package/module.py")
    assert_with_msg(
        str_result == "src.package.module",
        f"Expected 'src.package.module', got {str_result!r}",
    )

    assert_with_msg(
        to_module_name("package.module") == "package.module",
        f"Expected 'package.module', got {to_module_name('package.module')!r}",
    )

    # Test edge cases
    assert_with_msg(
        to_module_name(".") == "",
        f"Expected empty string for '.', got {to_module_name('.')!r}",
    )

    assert_with_msg(
        to_module_name("./") == "",
        f"Expected empty string for './', got {to_module_name('./')!r}",
    )

    assert_with_msg(
        to_module_name("") == "",
        f"Expected empty string for empty string, got {to_module_name('')!r}",
    )

    # Test with ModuleType
    sys_module_name = to_module_name(sys)
    assert_with_msg(
        sys_module_name == "sys", f"Expected 'sys', got {sys_module_name!r}"
    )


def test_to_path() -> None:
    """Test func for to_path."""
    # Test module name to path conversion
    result = to_path("src.package.module", is_package=False)
    expected = Path("src/package/module.py")
    assert_with_msg(result == expected, f"Expected {expected}, got {result}")

    # Test package path conversion
    result = to_path("src.package", is_package=True)
    expected = Path("src/package")
    assert_with_msg(result == expected, f"Expected {expected}, got {result}")

    # Test with Path input
    result = to_path(Path("src/package/module.py"), is_package=False)
    expected = Path("src/package/module.py")
    assert_with_msg(result == expected, f"Expected {expected}, got {result}")

    # Test with ModuleType
    result = to_path(sys, is_package=True)
    # sys module should resolve to a .py file path
    assert_with_msg(
        result.name == "sys",
        f"Expected sys module, got {result}",
    )


def test_create_module(tmp_path: Path) -> None:
    """Test func for create_module."""
    # Test creating a regular module
    with chdir(tmp_path):
        module_name = "test_package.test_module"
        module = create_module(module_name, is_package=False)
        assert_with_msg(
            isinstance(module, ModuleType),
            f"Expected module to be ModuleType, got {type(module)}",
        )

        # Test creating a package
        package_name = "test_package2"
        package = create_module(package_name, is_package=True)
        assert_with_msg(
            isinstance(package, ModuleType),
            f"Expected package to be ModuleType, got {type(package)}",
        )


def test_import_module_from_path(tmp_path: Path) -> None:
    """Test func for import_module_from_path."""
    # Create a temporary module file with known content
    with chdir(tmp_path):
        module_content = '''"""Test module."""

def test_function() -> str:
    """Test function."""
    return "test"

class TestClass:
    """Test class."""
    pass
'''
        module_file = tmp_path / "test_module.py"
        module_file.write_text(module_content)
        module = import_module_from_path(module_file)
        assert_with_msg(
            module.__name__ == "test_module", f"Expected module name, got {module}"
        )
        assert_with_msg(
            module.test_function() == "test",
            f"Expected test_function to return 'test', got {module.test_function()}",
        )

        # Test creating a package
        package_dir = tmp_path / "test_package"
        package_dir.mkdir()
        init_file = package_dir / "__init__.py"
        init_file.write_text('"""Test package."""\n')
        package = import_module_from_path(package_dir)
        assert_with_msg(
            package.__name__ == "test_package", f"Expected package name, got {package}"
        )

        # test with deeper path
        subdir = package_dir / "subdir"
        subdir.mkdir()
        init_file = subdir / "__init__.py"
        init_file.write_text('"""Test package."""\n')
        package = import_module_from_path(subdir)
        assert_with_msg(
            package.__name__ == "test_package.subdir",
            f"Expected package name, got {package}",
        )


def test_import_module_from_path_with_default(tmp_path: Path) -> None:
    """Test func for import_module_from_path_with_default."""
    # Create a temporary module file with known content
    with chdir(tmp_path):
        module_content = '''"""Test module."""

def test_function() -> str:
    """Test function."""
    return "test"

class TestClass:
    """Test class."""
    pass
'''

        module_file = tmp_path / "test_module.py"
        module_file.write_text(module_content)
        module = import_module_from_path_with_default(module_file)
        assert_with_msg(
            module.__name__ == "test_module", f"Expected module name, got {module}"
        )

        non_existing_file = tmp_path / "non_existing.py"
        module = import_module_from_path_with_default(
            non_existing_file, default="default"
        )
        assert_with_msg(module == "default", f"Expected default, got {module}")


def test_import_module_from_file(tmp_path: Path) -> None:
    """Test func for import_module_from_path."""
    # Create a temporary module file with known content
    with chdir(tmp_path):
        module_content = '''"""Test module."""

def test_function() -> str:
    """Test function."""
    return "test"

class TestClass:
    """Test class."""
    pass
'''
        module_file = tmp_path / "test_module.py"
        module_file.write_text(module_content)
        module = import_module_from_file(module_file)
        assert_with_msg(
            module.__name__ == "test_module", f"Expected module name, got {module}"
        )

        # test with deeper path
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        module_file = subdir / "test_module.py"
        module_file.write_text(module_content)
        module = import_module_from_file(module_file)
        assert_with_msg(
            module.__name__ == "subdir.test_module",
            f"Expected module name, got {module}",
        )


def test_make_obj_importpath() -> None:
    """Test func for make_obj_importpath."""

    # Test with a function
    def test_func() -> None:
        pass

    result = make_obj_importpath(test_func)
    expected = f"{test_func.__module__}.{test_func.__qualname__}"
    assert_with_msg(result == expected, f"Expected {expected}, got {result}")

    # Test with a class
    class TestClass:
        def test_method(self) -> None:
            pass

    result = make_obj_importpath(TestClass)
    expected = f"{TestClass.__module__}.{TestClass.__qualname__}"
    assert_with_msg(result == expected, f"Expected {expected}, got {result}")

    result = make_obj_importpath(TestClass.test_method)
    expected = f"{TestClass.__module__}.{TestClass.test_method.__qualname__}"
    assert_with_msg(result == expected, f"Expected {expected}, got {result}")

    # Test with a module
    result = make_obj_importpath(sys)
    assert_with_msg(result == "sys", f"Expected 'sys', got {result}")


def test_import_obj_from_importpath() -> None:
    """Test func for import_obj_from_importpath."""
    # Test importing a module

    result = import_obj_from_importpath("sys")

    assert_with_msg(
        result.__name__ == "sys" and hasattr(result, "path"),
        f"Expected sys module, got {result}",
    )

    # Test importing a function from a module
    result = import_obj_from_importpath("os.path.join")

    assert_with_msg(
        result is os.path.join, f"Expected os.path.join function, got {result}"
    )

    # Test importing a class
    result = import_obj_from_importpath("pathlib.Path")

    assert_with_msg(result is Path, f"Expected pathlib.Path class, got {result}")

    # Test error cases
    with pytest.raises(ImportError):
        import_obj_from_importpath("nonexistent.module")

    with pytest.raises(AttributeError):
        import_obj_from_importpath("sys.nonexistent_attr")


def test_get_isolated_obj_name() -> None:
    """Test func for get_isolated_obj_name."""
    # Test with a module
    result = get_isolated_obj_name(sys)
    assert_with_msg(result == "sys", f"Expected 'sys', got {result}")

    # Test with a nested module
    result = get_isolated_obj_name(os.path)
    # On Windows, os.path is ntpath; on Unix, it's posixpath
    expected_names = ["path", "ntpath", "posixpath"]
    assert_with_msg(
        result in expected_names,
        f"Expected one of {expected_names}, got {result}",
    )

    # Test with a class
    class TestClass:
        pass

    result = get_isolated_obj_name(TestClass)
    assert_with_msg(result == "TestClass", f"Expected 'TestClass', got {result}")

    # Test with a function
    def test_function() -> None:
        pass

    result = get_isolated_obj_name(test_function)
    assert_with_msg(
        result == "test_function", f"Expected 'test_function', got {result}"
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

    # Change to tmp_path directory and add to sys.path temporarily
    original_cwd = Path.cwd()
    original_path = sys.path[:]
    os.chdir(tmp_path)
    sys.path.insert(0, str(tmp_path))

    try:
        test_objs_module = import_module("test_objs_module")

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
        method_names = [obj.__name__ for obj in class_objs]
        assert_with_msg(
            "method1" in method_names,
            f"Expected 'method1' in class methods, got {method_names}",
        )

        # Test with non-module, non-class object
        def test_func() -> None:
            pass

        result = get_objs_from_obj(test_func)
        assert_with_msg(result == [], f"Expected empty list for function, got {result}")

    finally:
        # Clean up
        os.chdir(original_cwd)
        sys.path[:] = original_path
        if "test_objs_module" in sys.modules:
            del sys.modules["test_objs_module"]


def test_execute_all_functions_from_module(tmp_path: Path) -> None:
    """Test func for execute_all_functions_from_module."""
    # Create a test module with functions that return values
    module_content = '''"""Test module."""

def func1() -> str:
    """Function 1."""
    return "result1"

def func2() -> int:
    """Function 2."""
    return 42

def func3() -> None:
    """Function 3."""
    pass
'''

    # Create and import the module
    module_file = tmp_path / "test_exec_module.py"
    module_file.write_text(module_content)

    # Change to tmp_path directory and add to sys.path temporarily
    original_cwd = Path.cwd()
    original_path = sys.path[:]
    os.chdir(tmp_path)
    sys.path.insert(0, str(tmp_path))

    try:
        test_exec_module = import_module("test_exec_module")

        # Execute all functions
        results = execute_all_functions_from_module(test_exec_module)

        # Should have 3 results
        expected_exec_results_count = 3
        assert_with_msg(
            len(results) == expected_exec_results_count,
            f"Expected {expected_exec_results_count} results, got {len(results)}",
        )

        # Check that we got the expected return values
        assert_with_msg(
            "result1" in results, f"Expected 'result1' in results, got {results}"
        )

        test_return_value = 42
        assert_with_msg(
            test_return_value in results,
            f"Expected {test_return_value} in results, got {results}",
        )

        assert_with_msg(None in results, f"Expected None in results, got {results}")

    finally:
        # Clean up
        os.chdir(original_cwd)
        sys.path[:] = original_path
        if "test_exec_module" in sys.modules:
            del sys.modules["test_exec_module"]


def test_get_default_init_module_content() -> None:
    """Test func for get_default_init_module_content."""
    result = get_default_init_module_content()
    # assert is str
    assert_with_msg(isinstance(result, str), f"Expected str, got {type(result)}")


def test_get_default_module_content() -> None:
    """Test func for get_default_module_content."""
    result = get_default_module_content()
    # assert is str
    assert_with_msg(isinstance(result, str), f"Expected str, got {type(result)}")


def test_get_module_of_obj() -> None:
    """Test func for get_module_of_obj."""

    # Test with a function
    def test_function() -> None:
        pass

    module = get_module_of_obj(test_function)
    assert_with_msg(
        module.__name__ == __name__,
        f"Expected module name {__name__}, got {module.__name__}",
    )

    # Test with a class method
    class TestClass:
        def test_method(self) -> None:
            pass

        @property
        def test_property(self) -> str:
            return "test"

    method_module = get_module_of_obj(TestClass.test_method)
    assert_with_msg(
        method_module.__name__ == __name__,
        f"Expected module name {__name__}, got {method_module.__name__}",
    )

    # Test with a property
    prop_module = get_module_of_obj(TestClass.test_property)
    assert_with_msg(
        prop_module.__name__ == __name__,
        f"Expected module name {__name__}, got {prop_module.__name__}",
    )

    # Test with built-in function
    os_module = get_module_of_obj(os.path.join)
    assert_with_msg(
        "posixpath" in os_module.__name__ or "ntpath" in os_module.__name__,
        f"Expected posixpath or ntpath module, got {os_module.__name__}",
    )


def test_get_executing_module() -> None:
    """Test func for get_executing_module."""
    executing_module = get_executing_module()
    executing_file = executing_module.__file__
    if executing_file is None:
        msg = "Expected file to be not None"
        raise ValueError(msg)

    assert_with_msg(
        executing_module.__name__ == "__main__",
        f"Expected module name to be '__main__', got {executing_module.__name__}",
    )


def test_import_module_with_default() -> None:
    """Test func for import_module_with_default."""
    # Test importing a valid module
    result = import_module_with_default("sys")
    assert_with_msg(result.__name__ == "sys", f"Expected sys module, got {result}")

    # Test importing a non-existent module with a default
    result = import_module_with_default("nonexistent", default="default")
    assert_with_msg(result == "default", f"Expected default, got {result}")


def test_make_init_module(tmp_path: Path) -> None:
    """Test func for make_init_module."""
    with chdir(tmp_path):
        make_init_module(Path.cwd())
        assert_with_msg(
            (Path.cwd() / "__init__.py").exists(),
            "Expected __init__.py file to be created",
        )


def test_make_init_modules_for_package(tmp_path: Path, mocker: MockFixture) -> None:
    """Test func for make_init_modules_for_package."""
    # Create test directory structure
    test_package = tmp_path / "test_package"
    sub_dir1 = test_package / "subdir1"
    sub_dir2 = test_package / "subdir2"
    sub_dir1.mkdir(parents=True)
    sub_dir2.mkdir(parents=True)

    # Create an existing __init__.py in one directory
    (sub_dir1 / "__init__.py").write_text("# existing")

    # Mock to_path
    mock_to_path = mocker.patch(make_obj_importpath(to_path))
    mock_to_path.return_value = test_package


def test_make_dir_with_init_file(tmp_path: Path, mocker: MockFixture) -> None:
    """Test func for make_dir_with_init_file."""
    test_dir = tmp_path / "test_package"

    # Mock make_init_modules_for_package
    mock_make_init = mocker.patch(make_obj_importpath(make_init_modules_for_package))

    make_dir_with_init_file(test_dir)

    assert_with_msg(
        test_dir.exists() and test_dir.is_dir(),
        f"Expected directory {test_dir} to be created",
    )
    mock_make_init.assert_called_once_with(test_dir)


def test_make_pkg_dir(tmp_path: Path) -> None:
    """Test func for make_init_modules_for_path."""
    with chdir(tmp_path):
        mpath = Path.cwd() / "test" / "package"
        make_pkg_dir(mpath)
        assert_with_msg(
            (Path.cwd() / "test" / "__init__.py").exists(),
            "Expected __init__.py file to be created",
        )
        assert_with_msg(
            (Path.cwd() / "test" / "package" / "__init__.py").exists(),
            "Expected __init__.py file to be created",
        )
        assert_with_msg(
            not (Path.cwd() / "__init__.py").exists(),
            "Did not expect __init__.py file to be created",
        )


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
