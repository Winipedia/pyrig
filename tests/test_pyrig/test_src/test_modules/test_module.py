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

from pyrig.src.modules.module import (
    create_module,
    execute_all_functions_from_module,
    get_default_module_content,
    get_isolated_obj_name,
    get_module_content_as_str,
    get_module_name_replacing_start_module,
    import_module_from_file,
    import_module_with_default,
    import_module_with_file_fallback,
    import_module_with_file_fallback_with_default,
    import_obj_from_importpath,
    make_obj_importpath,
    module_has_docstring,
)


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
        assert result == module_content, (
            f"Expected module content to match, got {result!r}"
        )

    finally:
        # Clean up
        os.chdir(original_cwd)
        sys.path[:] = original_path
        if "test_module" in sys.modules:
            del sys.modules["test_module"]


def test_create_module(tmp_path: Path) -> None:
    """Test func for create_module."""
    # Test creating a regular module
    with chdir(tmp_path):
        module_path = tmp_path / "test_pkg.test_module.py"
        module = create_module(module_path)
        assert isinstance(module, ModuleType)
        assert module.__name__ == "test_pkg.test_module"
        assert module.__file__ == str(module_path)


def test_make_obj_importpath() -> None:
    """Test func for make_obj_importpath."""

    # Test with a function
    def test_func() -> None:
        pass

    result = make_obj_importpath(test_func)
    expected = f"{test_func.__module__}.{test_func.__qualname__}"
    assert result == expected, f"Expected {expected}, got {result}"

    # Test with a class
    class TestClass:
        def test_method(self) -> None:
            pass

    result = make_obj_importpath(TestClass)
    expected = f"{TestClass.__module__}.{TestClass.__qualname__}"
    assert result == expected, f"Expected {expected}, got {result}"

    result = make_obj_importpath(TestClass.test_method)
    expected = f"{TestClass.__module__}.{TestClass.test_method.__qualname__}"
    assert result == expected, f"Expected {expected}, got {result}"

    # Test with a module
    result = make_obj_importpath(sys)
    assert result == "sys", f"Expected 'sys', got {result}"


def test_import_obj_from_importpath() -> None:
    """Test func for import_obj_from_importpath."""
    # Test importing a module

    result = import_obj_from_importpath("sys")

    assert result == sys, f"Expected sys module, got {result}"
    assert hasattr(result, "path"), f"Expected sys module, got {result}"

    # Test importing a function from a module
    result = import_obj_from_importpath("os.path.join")

    assert result is os.path.join, f"Expected os.path.join function, got {result}"

    # Test importing a class
    result = import_obj_from_importpath("pathlib.Path")

    assert result is Path, f"Expected pathlib.Path class, got {result}"

    # Test error cases
    with pytest.raises(ImportError):
        import_obj_from_importpath("nonexistent.module")

    with pytest.raises(AttributeError):
        import_obj_from_importpath("sys.nonexistent_attr")


def test_get_isolated_obj_name() -> None:
    """Test func for get_isolated_obj_name."""
    # Test with a module
    result = get_isolated_obj_name(sys)
    assert result == "sys", f"Expected 'sys', got {result}"

    # Test with a nested module
    result = get_isolated_obj_name(os.path)
    # On Windows, os.path is ntpath; on Unix, it's posixpath
    expected_names = ["path", "ntpath", "posixpath"]
    assert result in expected_names, f"Expected one of {expected_names}, got {result}"

    # Test with a class
    class TestClass:
        pass

    result = get_isolated_obj_name(TestClass)
    assert result == "TestClass", f"Expected 'TestClass', got {result}"

    # Test with a function
    def test_function() -> None:
        pass

    result = get_isolated_obj_name(test_function)
    assert result == "test_function", f"Expected 'test_function', got {result}"


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
        assert len(results) == expected_exec_results_count, (
            f"Expected {expected_exec_results_count} results, got {len(results)}"
        )

        # Check that we got the expected return values
        assert "result1" in results, f"Expected 'result1' in results, got {results}"

        test_return_value = 42
        assert test_return_value in results, (
            f"Expected {test_return_value} in results, got {results}"
        )

        assert None in results, f"Expected None in results, got {results}"

    finally:
        # Clean up
        os.chdir(original_cwd)
        sys.path[:] = original_path
        if "test_exec_module" in sys.modules:
            del sys.modules["test_exec_module"]


def test_get_default_module_content() -> None:
    """Test func for get_default_module_content."""
    result = get_default_module_content()
    # assert is str
    assert isinstance(result, str), f"Expected str, got {type(result)}"


def test_import_module_with_default() -> None:
    """Test func for import_module_with_default."""
    # Test importing a valid module
    result = import_module_with_default("sys")
    assert result.__name__ == "sys", f"Expected sys module, got {result}"

    # Test importing a non-existent module with a default
    result = import_module_with_default("nonexistent", default="default")
    assert result == "default", f"Expected default, got {result}"


def test_get_module_name_replacing_start_module(mocker: MockFixture) -> None:
    """Test function."""
    mock_module = mocker.MagicMock(spec=ModuleType)
    mock_module.__name__ = "some.module.name"
    new_name = get_module_name_replacing_start_module(mock_module, "new")
    expected_new_name = "new.module.name"
    assert new_name == expected_new_name, (
        f"Expected {expected_new_name}, got {new_name}"
    )


def test_import_module_with_file_fallback(tmp_path: Path) -> None:
    """Test function."""
    with chdir(tmp_path):
        with pytest.raises(FileNotFoundError):
            import_module_with_file_fallback(Path("nonexistent.py"))
        # create a module
        module_file = tmp_path / "test_module.py"
        module_file.write_text('"""Test module."""\n')
        module = import_module_with_file_fallback(module_file)
        assert module.__name__ == "test_module"


def test_import_module_with_file_fallback_with_default(tmp_path: Path) -> None:
    """Test function."""
    with chdir(tmp_path):
        non_existing_file = tmp_path / Path("non_existing.py")
        assert not non_existing_file.exists()

        module = import_module_with_file_fallback_with_default(non_existing_file)
        assert module is None

        assert not non_existing_file.exists()

        module = import_module_with_file_fallback_with_default(
            non_existing_file, default="default"
        )
        assert module == "default"

        # create a module
        module_file = tmp_path / "test_module.py"
        module_file.write_text('"""Test module."""\n')
        module = import_module_with_file_fallback_with_default(module_file)
        assert module.__name__ == "test_module"


def test_import_module_from_file(tmp_path: Path) -> None:
    """Test function."""
    with chdir(tmp_path):
        non_existing_file = tmp_path / Path("non_existing.py")
        with pytest.raises(FileNotFoundError):
            import_module_from_file(non_existing_file)

        module_path = tmp_path / "test_module.py"
        module_path.write_text('"""Test module."""\n')
        module = import_module_from_file(module_path)
        assert module.__name__ == "test_module"

        module_pkg_path = tmp_path / "test_pkg" / "test_module.py"
        module_pkg_path.parent.mkdir()
        module_pkg_path.write_text('"""Test module."""\n')
        module = import_module_from_file(module_pkg_path)
        assert module.__name__ == "test_pkg.test_module"


def test_module_has_docstring(tmp_path: Path) -> None:
    """Test function."""
    with chdir(tmp_path):
        module_path = tmp_path / "test_module.py"
        module = create_module(module_path)
        assert module_has_docstring(module)

        module_path_no_docstring = tmp_path / "test_module_no_docstring.py"
        module_path_no_docstring.write_text("def test_function() -> str:\n    pass\n")
        module_no_docstring = create_module(module_path_no_docstring)
        assert not module_has_docstring(module_no_docstring)
