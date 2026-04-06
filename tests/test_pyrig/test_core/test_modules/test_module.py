"""module for the following module path (maybe truncated).

tests.test_pyrig.test_modules.test_module
"""

import os
import sys
from collections.abc import Callable
from contextlib import chdir
from importlib import import_module
from pathlib import Path
from types import ModuleType

import pytest
from pytest_mock import MockFixture

from pyrig.core.modules.module import (
    import_module_from_file,
    import_module_with_default,
    import_module_with_file_fallback,
    import_modules,
    import_obj_from_importpath,
    isolated_obj_name,
    make_obj_importpath,
    module_content,
    module_has_docstring,
    module_name_replacing_start_module,
    reimport_module,
)
from pyrig.rig.cli import subcommands


def test_module_content(tmp_path: Path) -> None:
    """Test function."""
    with chdir(tmp_path):
        module_path = tmp_path / "test_module.py"
        content = '"""Test module."""\n'
        module_path.write_text(content)
        module = import_module_from_file(module_path, name="test_module")
        assert module.__name__ == "test_module"
        assert module.__file__ == str(module_path)
        assert module.__doc__ == "Test module."

        content = module_content(module)
        assert content == '"""Test module."""\n'


def test_make_obj_importpath() -> None:
    """Test function."""

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
    """Test function."""
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


def test_isolated_obj_name() -> None:
    """Test function."""
    # Test with a module
    result = isolated_obj_name(sys)
    assert result == "sys", f"Expected 'sys', got {result}"

    # Test with a nested module
    result = isolated_obj_name(os.path)
    # On Windows, os.path is ntpath; on Unix, it's posixpath
    expected_names = ["path", "ntpath", "posixpath"]
    assert result in expected_names, f"Expected one of {expected_names}, got {result}"

    # Test with a class
    class TestClass:
        pass

    result = isolated_obj_name(TestClass)
    assert result == "TestClass", f"Expected 'TestClass', got {result}"

    # Test with a function
    def test_function() -> None:
        pass

    result = isolated_obj_name(test_function)
    assert result == "test_function", f"Expected 'test_function', got {result}"


def test_import_module_with_default() -> None:
    """Test function."""
    # Test importing a valid module
    result = import_module_with_default("sys")
    assert result.__name__ == "sys", f"Expected sys module, got {result}"

    # Test importing a non-existent module with a default
    result = import_module_with_default("nonexistent", default="default")
    assert result == "default", f"Expected default, got {result}"


def test_module_name_replacing_start_module(mocker: MockFixture) -> None:
    """Test function."""
    mock_module = mocker.MagicMock(spec=ModuleType)
    mock_module.__name__ = "some.module.name"
    new_name = module_name_replacing_start_module(mock_module, "new")
    expected_new_name = "new.module.name"
    assert new_name == expected_new_name, (
        f"Expected {expected_new_name}, got {new_name}"
    )


def test_import_module_with_file_fallback(tmp_path: Path) -> None:
    """Test function."""
    with chdir(tmp_path):
        with pytest.raises(FileNotFoundError):
            import_module_with_file_fallback(Path("nonexistent.py"), name="nonexistent")
        # create a module
        module_file = tmp_path / "test_module.py"
        module_file.write_text('"""Test module."""\n')
        module = import_module_with_file_fallback(module_file, name="test_module")
        assert module.__name__ == "test_module"


def test_import_module_from_file(tmp_path: Path) -> None:
    """Test function."""
    with chdir(tmp_path):
        non_existing_file = tmp_path / Path("non_existing.py")
        with pytest.raises(FileNotFoundError):
            import_module_from_file(non_existing_file, name="non_existing")

        module_path = tmp_path / "test_module.py"
        module_path.write_text('"""Test module."""\n')
        module = import_module_from_file(module_path, name="test_module")
        assert module.__name__ == "test_module"

        module_package_path = tmp_path / "test_package" / "test_module.py"
        module_package_path.parent.mkdir()
        module_package_path.write_text('"""Test module."""\n')
        module = import_module_from_file(
            module_package_path, name="test_package.test_module"
        )
        assert module.__name__ == "test_package.test_module"


def test_module_has_docstring(
    tmp_path: Path, create_module: Callable[[Path], ModuleType]
) -> None:
    """Test function."""
    with chdir(tmp_path):
        module_path = Path("test_module.py")
        module = create_module(module_path)
        module_path.write_text('"""Test module."""\n')
        assert module_has_docstring(module)

        module_path_no_docstring = Path("test_module_no_docstring.py")
        module_path_no_docstring.write_text("def test_function() -> str:\n    pass\n")
        module_no_docstring = create_module(module_path_no_docstring)
        assert not module_has_docstring(module_no_docstring)


def test_import_modules() -> None:
    """Test function."""
    names = ["sys", "os"]
    modules = tuple(import_modules(names))

    assert modules == (sys, os)


def test_reimport_module() -> None:
    """Test function."""
    mod1 = import_module(subcommands.__name__)
    mod2 = reimport_module(subcommands)
    assert mod1 is not mod2
