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
from pytest_mock import MockerFixture

import pyrig
from pyrig.core.introspection import modules
from pyrig.core.introspection.modules import (
    callable_obj_import_path,
    import_module_from_file,
    import_module_with_default,
    import_module_with_file_fallback,
    import_modules,
    iter_modules,
    leaf_module_name,
    module_content,
    module_has_docstring,
    module_name_replacing_start_module,
    reimport_module,
    root_module,
)
from pyrig.core.introspection.packages import import_package_with_dir_fallback
from pyrig.rig.cli import subcommands


def test_module_content(tmp_path: Path) -> None:
    """Test function."""
    module_name = test_module_content.__name__
    with chdir(tmp_path):
        module_path = tmp_path / f"{module_name}.py"
        content = '"""Test module."""\n'
        module_path.write_text(content)
        module = import_module_from_file(module_path, name=module_name)
        assert module.__name__ == module_name
        assert module.__file__ == str(module_path)
        assert module.__doc__ == "Test module."

        content = module_content(module)
        assert content == '"""Test module."""\n'


def test_import_module_with_default() -> None:
    """Test function."""
    # Test importing a valid module
    result = import_module_with_default("sys")
    assert result.__name__ == "sys", f"Expected sys module, got {result}"

    # Test importing a non-existent module with a default
    result = import_module_with_default("nonexistent", default="default")
    assert result == "default", f"Expected default, got {result}"


def test_module_name_replacing_start_module(mocker: MockerFixture) -> None:
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
    module_name = test_import_module_with_file_fallback.__name__
    with chdir(tmp_path):
        with pytest.raises(FileNotFoundError):
            import_module_with_file_fallback(Path("nonexistent.py"), name="nonexistent")
        # create a module
        module_file = tmp_path / f"{module_name}.py"
        module_file.write_text('"""Test module."""\n')
        module = import_module_with_file_fallback(module_file, name=module_name)
        assert module.__name__ == module_name


def test_import_module_from_file(tmp_path: Path, mocker: MockerFixture) -> None:
    """Test function."""
    with chdir(tmp_path):
        non_existing_file = tmp_path / Path("non_existing.py")
        with pytest.raises(FileNotFoundError):
            import_module_from_file(non_existing_file, name="non_existing")
        assert "non_existing" not in sys.modules, (
            "Module should not be in sys.modules after failed import"
        )
        module_name = test_import_module_from_file.__name__
        module_path = tmp_path / f"{module_name}.py"
        module_path.write_text('"""Test module."""\n')
        module = import_module_from_file(module_path, name=module_name)
        assert module.__name__ == module_name

        module_package_name = f"{module_name}_package.{module_name}"
        module_package_path = tmp_path / f"{module_name}_package" / f"{module_name}.py"
        module_package_path.parent.mkdir()
        module_package_path.write_text('"""Test module."""\n')
        module = import_module_from_file(module_package_path, name=module_package_name)
        assert module.__name__ == module_package_name

        # mock spec_from_loader to return None to test ImportError
        spec_from_loader_mock = mocker.patch(
            modules.__name__ + ".spec_from_loader", return_value=None
        )
        with pytest.raises(ImportError):
            import_module_from_file(module_path, name=module_name)
        spec_from_loader_mock.assert_called_once()


def test_module_has_docstring(
    tmp_path: Path, create_module: Callable[[Path], ModuleType]
) -> None:
    """Test function."""
    module_name = test_module_has_docstring.__name__
    with chdir(tmp_path):
        module_path = Path(f"{module_name}.py")
        module_path.write_text('"""Test module."""\n')
        module = create_module(module_path)
        assert module_has_docstring(module)

        module_path_no_docstring = Path(f"{module_name}_no_docstring.py")
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


def test_leaf_module_name() -> None:
    """Test function."""
    assert leaf_module_name(subcommands) == "subcommands"


def test_callable_obj_import_path() -> None:
    """Test function."""
    assert (
        callable_obj_import_path(subcommands.sync) == "pyrig.rig.cli.subcommands.sync"
    )


def test_iter_modules(tmp_path: Path) -> None:
    """Test function."""
    # Create a temporary package with known content
    with chdir(tmp_path):
        package_dir = tmp_path / test_iter_modules.__name__
        package_dir.mkdir()
        init_file = package_dir / "__init__.py"
        init_file.write_text('"""Test package."""\n')
        module_file = package_dir / "test_module.py"
        module_file.write_text('"""Test module."""\n')
        package = import_package_with_dir_fallback(
            package_dir, name=test_iter_modules.__name__
        )

        modules = iter_modules(package)
        modules_names = [m.__name__ for m, _ in modules]
        assert modules_names == [package.__name__ + ".test_module"], (
            f"Expected [package.test_module], got {modules}"
        )


def test_root_module() -> None:
    """Test function."""
    assert root_module(subcommands) is pyrig
